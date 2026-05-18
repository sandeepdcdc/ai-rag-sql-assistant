from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
from sqlalchemy import text

from db import engine
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import text

# from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq

from db import engine

from dotenv import load_dotenv

load_dotenv()

from schema_config import (
    business_schema,
    relationships
)

from rag_engine import (
    retrieve_relevant_tables
)

from prompts import (
    get_sql_prompt,
    get_correction_prompt
)

from sql_validator import (
    validate_sql
)

from utils import (
    detect_limit,
    clean_sql
)

# =====================================================
# FASTAPI Application
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
# LLM
# =====================================================
print(os.getenv("GROQ_API_KEY"))
# llm = OllamaLLM(
#     model="qwen2.5:3b"
# )
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

# =====================================================
# REQUEST MODEL
# =====================================================

class QuestionRequest(BaseModel):

    question: str

# =====================================================
# API
# =====================================================

@app.post("/ask")

def ask_question(request: QuestionRequest):

    question = request.question

    question_lower = question.lower()

    limit_value = detect_limit(question)

    # =====================================================
    # RAG TABLE RETRIEVAL
    # =====================================================

    relevant_tables = (
        retrieve_relevant_tables(question)
    )

    # =====================================================
    # SEMANTIC DETECTION
    # =====================================================

    if "full name" in question_lower:

        relevant_tables.append(
            "dc_patients"
        )

    if "branch name" in question_lower:

        relevant_tables.append(
            "dc_branch"
        )

    if "state" in question_lower:

        relevant_tables.append(
            "dc_states"
        )

    relevant_tables = list(
        set(relevant_tables)
    )

    # =====================================================
    # BUILD MINIMAL SCHEMA
    # =====================================================

    minimal_schema = ""

    for table in relevant_tables:

        minimal_schema += (
            f"\nTable: {table}\n"
        )

        for col in business_schema[table]:

            minimal_schema += (
                f"- {table}.{col}\n"
            )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    relationship_prompt = ""

    if len(relevant_tables) > 1:

        relationship_prompt = relationships

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = get_sql_prompt(
        minimal_schema,
        relationship_prompt,
        limit_value,
        question
    )

    # =====================================================
    # GENERATE SQL
    # =====================================================

    response = llm.invoke(prompt)
    sql_query = response.content
    sql_query = clean_sql(sql_query)

    # =====================================================
    # VALIDATE SQL
    # =====================================================

    validate_sql(sql_query)

    # =====================================================
    # EXECUTE SQL
    # =====================================================

    try:

        result_df = pd.read_sql(
            text(sql_query),
            engine
        )

    except Exception as e:

        correction_prompt = (
            get_correction_prompt(
                question,
                sql_query,
                e,
                minimal_schema,
                relationship_prompt
            )
        )

        corrected_sql = llm.invoke(
            correction_prompt
        )

        corrected_sql = clean_sql(
            corrected_sql
        )

        validate_sql(corrected_sql)

        result_df = pd.read_sql(
            text(corrected_sql),
            engine
        )

        sql_query = corrected_sql

    return {
        "question": question,
        "sql": sql_query,
        "tables": relevant_tables,
        "result": result_df.astype(str).to_dict(
            orient="records"
        )
    }

def execute_query(sql_query):

    result_df = pd.read_sql(
        text(sql_query),
        engine
    )

    return result_df