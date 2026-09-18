"""
SQL file runner for local DuckDB analysis.

Purpose:
Run a SQL file against the project's local DuckDB database and
print any result-producing statements to the terminal.

Usage:
python query.py <sql_file>

Example:
python query.py sql/validation.sql

The script is intended as a lightweight development utility for
running and inspecting SQL during the analysis workflow. It is not
part of the core experiment pipeline.
"""

import sys
import duckdb

if len(sys.argv) != 2:
print("Usage: python query.py <sql_file>")
sys.exit(1)

sql_file = sys.argv[1]

con = duckdb.connect("analytics.duckdb")

with open(sql_file, "r") as file:
sql = file.read()

statements = [
statement.strip()
for statement in sql.split(";")
if statement.strip()
]

for statement in statements:
result = con.execute(statement)

```
if result.description:
    print()
    print(result.fetchdf().to_string(index=False))
```

con.close()
