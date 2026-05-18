def get_sql_prompt(
    minimal_schema,
    relationship_prompt,
    limit_value,
    question
):

    return f"""
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
15. For text filtering use LIKE '%value%'
16. Never assume dates/months
17. Never add unnecessary conditions

Question:
{question}
"""


def get_correction_prompt(
    question,
    sql_query,
    error,
    minimal_schema,
    relationship_prompt
):

    return f"""
You are a MySQL SQL fixer.

Original Question:
{question}

Failed SQL:
{sql_query}

SQL Error:
{str(error)}

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
9. Always return descriptive column aliases.
10. If month number is used, also return month name.
11. If branch_id is used, include branch_name.
12. If state_id is used, include state_name.
13. Never return only IDs when related name columns exist.
14. Use readable aliases like:
   - Billing Count
   - Month
   - Branch Name
   - State Name
15. Prefer business-friendly output over technical output.
16. Use MONTHNAME() whenever month is grouped.

EXAMPLE -
Question:
top 3 months billing count in 2025 for branch id 1

SQL:
SELECT
    MONTHNAME(billing_date) AS Month,
    COUNT(patient_id) AS Billing_Count
FROM dc_patient_billing
WHERE branch_id = 1
AND YEAR(billing_date) = 2025
GROUP BY MONTH(billing_date), MONTHNAME(billing_date)
ORDER BY Billing_Count DESC
LIMIT 3;

Corrected SQL:
"""