def validate_sql(sql_query):

    blocked_keywords = [
        "DELETE",
        "DROP",
        "UPDATE",
        "INSERT",
        "TRUNCATE",
        "ALTER"
    ]

    sql_upper = sql_query.upper()

    for keyword in blocked_keywords:

        if keyword in sql_upper:

            raise Exception(
                f"Blocked unsafe SQL keyword: {keyword}"
            )

    return True