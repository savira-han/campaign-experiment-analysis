import duckdb


con = duckdb.connect("analytics.duckdb")


with open("sql/experiment_metrics.sql", "r") as file:
    experiment_sql = file.read()

con.execute(experiment_sql)


with open("sql/validation.sql", "r") as file:
    validation_sql = file.read()


queries = validation_sql.split(";")

for query in queries:
    query = query.strip()

    if not query:
        continue

    result = con.execute(query).fetchdf()

    print()
    print(result.to_string(index=False))


con.close()