from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# =====================================================
# BUSINESS SCHEMA DOCUMENTS
# =====================================================

schema_docs = [

    {
        "table": "dc_patient_billing",
        "text": """
        patient billing records
        billing transactions
        billing_date
        branch billing
        patient payments
        branch_name
        """
    },

    {
        "table": "dc_branch",
        "text": """
        branch details
        city information
        branch location
        state_id
        active branches
        """
    },

    {
        "table": "dc_states",
        "text": """
        state details
        geography
        location region
        state_name
        """
    },

    {
        "table": "dc_patients",
        "text": """
        patient details
        demographics
        gender
        mobile number
        patient status
        """
    },

    {
        "table": "dc_patient_permission",
        "text": """
        dialysis frequency
        dialysis_per_week
        patient dialysis schedule
        permissions
        """
    }
]

# =====================================================
# LOAD EMBEDDING MODEL
# =====================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================================
# CREATE EMBEDDINGS
# =====================================================

texts = [doc["text"] for doc in schema_docs]

embeddings = model.encode(texts)

# =====================================================
# CREATE FAISS INDEX
# =====================================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

# =====================================================
# SAVE INDEX
# =====================================================

faiss.write_index(index, "schema_index.faiss")

# save metadata
with open("schema_docs.pkl", "wb") as f:

    pickle.dump(schema_docs, f)

print("\nSchema vector DB created successfully.")