from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import faiss
import pickle
import numpy as np
import urllib.parse
import os

from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

# =====================================================
# FASTAPI
# =====================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =====================================================
# LOAD ENV
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
# LOAD EMBEDDINGS
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
# SCHEMA
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
# RELATIONSHIPS
# =====================================================

relationships = """

1. dc_patient_billing.branch_id = dc_branch.branch_id

2. dc_branch.state_id = dc_states.state_id

3. dc_patients.branch_id = dc_branch.branch_id

4. dc_patient_permission.patient_id = dc_patients.patient_id

5. dc_patient_billing.patient_id = dc_patients.patient_id

"""

# =====================================================
# REQUEST MODEL
# =====================================================

class QueryRequest(BaseModel):
    question: str

# =====================================================
# API ENDPOINT
# =====================================================

@app.post("/ask")

def ask_question(request: QueryRequest):

    question = request.question

    # =================================================
    # SEMANTIC RETRIEVAL
    # =================================================

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

    # =================================================
    # BUILD SCHEMA
    # =================================================

    minimal_schema = ""

    for table in relevant_tables:

        minimal_schema += f"\nTable: {table}\n"

        for col in business_schema[table]:

            minimal_schema += f"- {table}.{col}\n"

    # =================================================
    # PROMPT
    # =================================================

    prompt = f"""
    You are an expert MySQL SQL generator.

    Database Schema:

    {minimal_schema}

    Relationships:

    {relationships}

    IMPORTANT RULES:

    1. Use ONLY provided tables and columns.
    2. Do NOT invent columns.
    3. Do NOT invent joins.
    4. Do NOT add unnecessary filters.
    5. Do NOT assume months/dates unless explicitly asked.
    6. If all required columns exist in one table, DO NOT use JOIN.
    7. Use JOIN only when required columns are missing.
    8. Return ONLY valid MySQL SQL.
    9. Do NOT explain anything.
   10. Do NOT add markdown.
   11. Use LIMIT only if user asks top/bottom.
   12. Never use PostgreSQL syntax.
   13. Never use UUID casting.
   14. Never add random conditions.
   15. For aggregation queries:
        - use GROUP BY correctly
        - use COUNT(*) correctly

   USER QUESTION:
   {question}

    SQL:
    """

    # =================================================
    # GENERATE SQL
    # =================================================

    sql_query = llm.invoke(prompt)

    sql_query = (
        sql_query
        .replace("```sql", "")
        .replace("```", "")
        .split("--")[0]
        .strip()
    )

    # =================================================
    # EXECUTE SQL
    # =================================================

    try:

        result_df = pd.read_sql(
            text(sql_query),
            engine
        )

        return {
            "question": question,
            "sql": sql_query,
            "tables": relevant_tables,
            "result": result_df.to_dict(
                orient="records"
            )
        }

    except Exception as e:

        return {
            "error": str(e),
            "sql": sql_query
        }