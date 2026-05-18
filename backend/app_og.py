import os
import re
import urllib.parse
import pandas as pd
import faiss
import pickle
import numpy as np
from db import engine

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# =====================================================
# MYSQL CONNECTION
# =====================================================

encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

connection_string = (
    f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    connection_string,
    pool_pre_ping=True,
    pool_recycle=3600
)

# =====================================================
# LOAD LLM
# =====================================================

llm = OllamaLLM(
    model="qwen2.5:3b"
)

# =====================================================
# LOAD EMBEDDING MODEL
# =====================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================================
# LOAD VECTOR DB
# =====================================================

index = faiss.read_index(
    "schema_index.faiss"
)

with open("schema_docs.pkl", "rb") as f:

    schema_docs = pickle.load(f)

# =====================================================
# ACTUAL BUSINESS SCHEMA
# =====================================================

business_schema = {

    "dc_patient_billing": [
        "patient_id",
        "p_first_name",
        "p_last_name",
        "branch_id",
        "branch_name",
        "billing_date"
    ],

    "dc_branch": [
        "branch_id",
        "branch_name",
        "state_id",
        "city_name",
        "is_active"
    ],

    "dc_states": [
        "state_id",
        "state_name"
    ],

    "dc_patients": [
        "patient_id",
        "patient_status_id",
        "branch_id",
        "full_name",
        "gender",
        "mobile_no",
        "dob",
        "status_id",
        "inactive_reason_id"
    ],

    "dc_patient_permission": [
        "patient_id",
        "dialysis_per_week"
    ]
}

# =====================================================
# SEMANTIC BUSINESS MODEL
# =====================================================

semantic_model = {

    "patient_full_name": {
        "table": "dc_patients",
        "column": "full_name"
    },

    "branch_name": {
        "table": "dc_branch",
        "column": "branch_name"
    },

    "state_name": {
        "table": "dc_states",
        "column": "state_name"
    },

    "billing_date": {
        "table": "dc_patient_billing",
        "column": "billing_date"
    },

    "dialysis_per_week": {
        "table": "dc_patient_permission",
        "column": "dialysis_per_week"
    }

}

# =====================================================
# RELATIONSHIPS
# =====================================================

relationships = """

1. dc_patient_billing.branch_id = dc_branch.branch_id

2. dc_branch.state_id = dc_states.state_id

3. dc_patients.branch_id = dc_branch.branch_id

4. dc_patient_permission.patient_id = dc_patients.patient_id

5. dc_patient_billing.patient_id = dc_patients.patient_id

"""

print("\nAVAILABLE TABLES:\n")
print(list(business_schema.keys()))

# =====================================================
# USER QUESTION
# =====================================================

question = input("\nAsk your database question:\n")

question_lower = question.lower()

# =====================================================
# DETECT LIMIT
# =====================================================

limit_match = re.search(r'\b(\d+)\b', question)

if limit_match:
    limit_value = limit_match.group(1)
else:
    limit_value = "5"

# =====================================================
# SEMANTIC TABLE RETRIEVAL
# =====================================================

question_embedding = embedding_model.encode(
    [question]
)

D, I = index.search(
    np.array(question_embedding),
    k=3
)

relevant_tables = []

for idx in I[0]:

    table_name = schema_docs[idx]["table"]

    if table_name not in relevant_tables:

        relevant_tables.append(table_name)

print("\nSEMANTICALLY RETRIEVED TABLES:\n")
print(relevant_tables)

# =====================================================
# SEMANTIC BUSINESS DETECTION
# =====================================================

force_join = False

# patient full name
if "full name" in question_lower:

    relevant_tables.append("dc_patients")

# branch name
if "branch name" in question_lower:

    relevant_tables.append("dc_branch")

# state name
if "state" in question_lower:

    relevant_tables.append("dc_states")

# remove duplicates
relevant_tables = list(set(relevant_tables))

# if multiple semantic entities exist
if len(relevant_tables) > 1:

    force_join = True

# =====================================================
# DETECT SINGLE TABLE POSSIBILITY
# =====================================================

single_table_possible = False
best_table = None

for table in relevant_tables:

    cols = business_schema[table]

    matched_cols = 0

    for word in question_lower.split():

        for col in cols:

            if word in col.lower():

                matched_cols += 1

    if matched_cols >= 2:

        single_table_possible = True
        best_table = table
        break

# =====================================================
# FORCE SINGLE TABLE IF POSSIBLE
# =====================================================

if single_table_possible and not force_join:

    relevant_tables = [best_table]

# =====================================================
# PRINT TABLES
# =====================================================

print("\nFINAL TABLES USED:\n")
print(relevant_tables)

# =====================================================
# BUILD MINIMAL SCHEMA
# =====================================================

minimal_schema = ""

for table in relevant_tables:

    minimal_schema += f"\nTable: {table}\n"

    for col in business_schema[table]:

        minimal_schema += f"- {table}.{col}\n"

print("\nMINIMAL SCHEMA:\n")
print(minimal_schema)

# =====================================================
# RELATIONSHIP CONTROL
# =====================================================

relationship_prompt = ""

if len(relevant_tables) > 1:

    relationship_prompt = relationships

# =====================================================
# SQL GENERATION PROMPT
# =====================================================

prompt = f"""
You are an expert MySQL SQL generator.

Database Schema:

{minimal_schema}

Relationships:

{relationship_prompt}

STRICT RULES:

1. Use ONLY tables from schema
2. Use ONLY exact column names
3. Never invent columns
4. Never invent tables
5. Never use markdown
6. Never explain anything
7. Never use aliases
8. Never use backticks
9. Use JOIN only if multiple tables provided
10. If single table provided, NEVER use JOIN
11. Use LIMIT {limit_value}
12. Use GROUP BY for aggregations
13. Use ORDER BY for top/bottom queries
14. Return ONLY executable MySQL query
15. For text filtering use LIKE '%value%' instead of exact =
16. For state/city/branch name searches use flexible matching with LIKE

Question:
{question}
"""

# =====================================================
# GENERATE SQL
# =====================================================

print("\nGenerating SQL...\n")

sql_query = llm.invoke(prompt)

# =====================================================
# CLEAN SQL
# =====================================================

sql_query = (
    sql_query
    .replace("```sql", "")
    .replace("```", "")
    .split("--")[0]
    .strip()
)

# auto fixes
sql_query = sql_query.replace(
    "COUNT(dc_patient_billing.*)",
    "COUNT(*)"
)

sql_query = sql_query.replace(
    "count(dc_patient_billing.*)",
    "COUNT(*)"
)

print("GENERATED SQL:\n")
print(sql_query)

# =====================================================
# SQL SAFETY CHECK
# =====================================================

blocked_keywords = [
    "DELETE",
    "DROP",
    "UPDATE",
    "INSERT",
    "TRUNCATE",
    "ALTER"
]

if any(keyword in sql_query.upper() for keyword in blocked_keywords):

    print("\nBlocked unsafe SQL query.")
    exit()

# =====================================================
# EXECUTE SQL
# =====================================================

try:

    result_df = pd.read_sql(
        text(sql_query),
        engine
    )

    print("\nQUERY RESULT:\n")
    print(result_df)

# =====================================================
# AUTO SQL CORRECTION
# =====================================================

except Exception as e:

    print("\nSQL EXECUTION ERROR:\n")
    print(e)

    correction_prompt = f"""
You are a MySQL SQL fixer.

Original Question:
{question}

Failed SQL:
{sql_query}

SQL Error:
{str(e)}

Database Schema:
{minimal_schema}

Relationships:
{relationship_prompt}

RULES:

1. Fix SQL completely
2. Preserve business meaning
3. Use ONLY exact columns
4. Use ONLY provided tables
5. Never invent columns
6. Never invent tables
7. Never explain anything
8. Return ONLY executable MySQL query

Corrected SQL:
"""

    print("\nAttempting SQL correction...\n")

    corrected_sql = llm.invoke(correction_prompt)

    corrected_sql = (
        corrected_sql
        .replace("```sql", "")
        .replace("```", "")
        .split("--")[0]
        .strip()
    )

    corrected_sql = corrected_sql.replace(
        "COUNT(dc_patient_billing.*)",
        "COUNT(*)"
    )

    print("CORRECTED SQL:\n")
    print(corrected_sql)

    # =====================================================
    # RETRY EXECUTION
    # =====================================================

    try:

        corrected_result = pd.read_sql(
            text(corrected_sql),
            engine
        )

        print("\nCORRECTED QUERY RESULT:\n")
        print(corrected_result)

    except Exception as retry_error:

        print("\nCORRECTION FAILED:\n")
        print(retry_error)