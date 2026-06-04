import sqlite3
from datetime import datetime


def write_dfs_to_gpkg(conn: sqlite3.Connection, tables: dict):
    cursor = conn.cursor()

    for table_name, df in tables.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        cursor.execute(
            "DELETE FROM gpkg_contents WHERE table_name = ?", (table_name,)
        )

        # 3. Registreren in gpkg_contents
        cursor.execute(
            """
            INSERT INTO gpkg_contents (
                table_name,
                data_type,
                identifier,
                description,
                last_change
            )
            VALUES (?, 'attributes', ?, '', ?)
            """,
            (
                table_name,
                table_name,
                datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            ),
        )

    conn.commit()
