import re


def detect_limit(question):

    limit_match = re.search(
        r'\b(\d+)\b',
        question
    )

    if limit_match:

        return limit_match.group(1)

    return "5"


def clean_sql(sql_query):

    sql_query = (
        sql_query
        .replace("```sql", "")
        .replace("```", "")
        .split("--")[0]
        .strip()
    )

    sql_query = sql_query.replace(
        "COUNT(dc_patient_billing.*)",
        "COUNT(*)"
    )

    sql_query = sql_query.replace(
        "count(dc_patient_billing.*)",
        "COUNT(*)"
    )

    return sql_query