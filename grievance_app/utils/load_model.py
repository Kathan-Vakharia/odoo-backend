from config.database import create_db_conn, close_conn
import os
import json

conn = create_db_conn()


def load_model(models_json: str, conn):

    cursor = conn.cursor()
    files = os.listdir(models_json)

    pointer = 0

    while pointer < len(files):

        fpath = os.path.join(models_json, files[pointer])

        f = open(fpath, 'r')
        table_data = json.load(f)
        f.close()

        table_name = table_data["table_name"]
        columns = table_data["columns"]

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for col in columns:
            col_name = col["name"]
            col_type = col["type"]
            col_constraints = col["constraints"]

            query += f"{col_name} {col_type} {col_constraints},"

        query = query.rstrip(",") + ")"

        try:

            # Execute the query
            cursor.execute(query)

            # Committing the changes
            conn.commit()

            files.remove(files[pointer])

        except Exception as e:
            print("Table ", table_name)
            print("Query" , query)
            print(e)
            pass

        pointer += 1
        if pointer >= len(files):
            pointer = 0


load_model("./models", conn)
