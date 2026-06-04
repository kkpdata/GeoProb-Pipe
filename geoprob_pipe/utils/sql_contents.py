import sqlite3
from datetime import datetime

import pandas as pd


def _create_table_with_pk(conn, table_name, df):
    cursor = conn.cursor()

    # Verwijder bestaande tabel
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    # SQLite types bepalen
    cols_sql = []
    for col, dtype in df.dtypes.items():
        if "int" in str(dtype):
            sql_type = "INTEGER"
        elif "float" in str(dtype):
            sql_type = "REAL"
        else:
            sql_type = "TEXT"

        cols_sql.append(f'"{col}" {sql_type}')

    cols_sql = ", ".join(cols_sql)

    # Setup primary key
    cursor.execute(f'''
        CREATE TABLE "{table_name}" (
            fid INTEGER PRIMARY KEY AUTOINCREMENT,
            {cols_sql}
        )
    ''')

def _register_gpkg_data_columns(conn, table_name):
    cursor = conn.cursor()

    # Haal kolomnamen op via SQLite pragma
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns = cursor.fetchall()

    for col in columns:
        col_name = col[1]  # tweede veld = column name

        cursor.execute(
            """
            INSERT OR REPLACE INTO gpkg_data_columns (
                table_name,
                column_name,
                name,
                title,
                description,
                mime_type,
                constraint_name
            )
            VALUES (?, ?, ?, ?, '', NULL, NULL)
            """,
            (
                table_name,
                col_name,
                col_name,
                col_name,
            ),
        )

def write_dfs_to_gpkg(conn: sqlite3.Connection, tables: dict[str, pd.DataFrame]):
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpkg_data_columns (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            name TEXT,
            title TEXT,
            description TEXT,
            mime_type TEXT,
            constraint_name TEXT,
            PRIMARY KEY (table_name, column_name)
        )
        """)

    for table_name, df in tables.items():
        if df.empty:  # Sla lege df over, dit breekt de SQL
            continue
        
        _create_table_with_pk(conn, table_name, df)
        
        df.to_sql(table_name, conn, if_exists="append", index=False)

        cursor.execute(
            "DELETE FROM gpkg_contents WHERE table_name = ?", (table_name,)
        )

        # Registreren in gpkg_contents
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

        _register_gpkg_data_columns(conn, table_name)

    conn.commit()
