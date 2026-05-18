import faiss
import pickle
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

index = faiss.read_index(
    "schema_index.faiss"
)

with open("schema_docs.pkl", "rb") as f:

    schema_docs = pickle.load(f)


def retrieve_relevant_tables(
    question,
    k=3
):

    question_embedding = (
        embedding_model.encode([question])
    )

    D, I = index.search(
        np.array(question_embedding),
        k=k
    )

    relevant_tables = []

    for idx in I[0]:

        table_name = schema_docs[idx]["table"]

        if table_name not in relevant_tables:

            relevant_tables.append(
                table_name
            )

    return relevant_tables