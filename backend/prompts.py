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

1. Use ONLY tables from schema
2. Use ONLY exact column names
3. Never invent columns
4. Never invent tables
5. Never use markdown
6. Never explain anything
7. Never use backticks
8. Use JOIN only if multiple tables required
9. If single table is sufficient, avoid unnecessary JOIN
10. Use LIMIT {limit_value}
11. Use GROUP BY for aggregations
12. Use ORDER BY for top/bottom queries
13. Return ONLY executable MySQL query
14. For text filtering use LIKE '%value%'
15. Never add unnecessary conditions

16. Always use business-friendly aliases

17. Every aggregate column MUST use aliases

Examples:
COUNT(*) AS billing_count
SUM(amount) AS total_amount
AVG(amount) AS average_amount

18. Never return raw aggregate expressions like:
COUNT(table.column)

19. If branch_name is returned, also include branch_id

20. If state_name is returned, also include state_id

21. If month is used:
Use:
MONTHNAME(date_column) AS month

22. Use readable aliases like:
branch_id
branch_name
billing_count
state_name
month

23. Prefer business-friendly output instead of technical output

EXAMPLES:

Question:
top 3 branches by billing count in January 2025

SQL:
SELECT
    branch_id,
    branch_name,
    COUNT(patient_id) AS billing_count
FROM dc_patient_billing
WHERE MONTH(billing_date) = 1
AND YEAR(billing_date) = 2025
GROUP BY branch_id, branch_name
ORDER BY billing_count DESC
LIMIT 3;


Question:
top 5 states by billing count in 2025

SQL:
SELECT
    s.state_id,
    s.state_name,
    COUNT(pb.patient_id) AS billing_count
FROM dc_states s
JOIN dc_branch b
ON s.state_id = b.state_id
JOIN dc_patient_billing pb
ON b.branch_id = pb.branch_id
WHERE YEAR(pb.billing_date) = 2025
GROUP BY s.state_id, s.state_name
ORDER BY billing_count DESC
LIMIT 5;
THIS WILL FIX

✅ missing branch_id
✅ ugly COUNT(column) names
✅ inconsistent aliases
✅ technical output
✅ month number issues
✅ missing state names
✅ inconsistent grouping

EXPECTED RESULT

Question:

top 3 branches by billing count in January 2025

Generated SQL:

SELECT
    branch_id,
    branch_name,
    COUNT(patient_id) AS billing_count
FROM dc_patient_billing
WHERE MONTH(billing_date) = 1
AND YEAR(billing_date) = 2025
GROUP BY branch_id, branch_name
ORDER BY billing_count DESC
LIMIT 3;

Frontend result:

Branch ID	Branch Name	Billing Count

Corrected SQL:
"""