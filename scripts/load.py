import sqlite3
import os

DB_PATH = "data/ecommerce.db"

def get_connection():
    """
    Returns a connection to the SQLite database.
    Creates the file if it doesn't exist.
    """
    connection = sqlite3.connect(DB_PATH)
    return connection


def load_dataframe(df, table_name, connection):
    """
    Loads a Pandas DataFrame into a SQLite table.
    Replaces the table completely on every run.
    """
    df.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False
    )
    print(f"Loaded {len(df)} rows into table: {table_name}")


def load(merged_df, users_df, revenue_per_user,
         revenue_by_country, daily_revenue):
    """
    Loads all DataFrames into SQLite database.
    """
    print("\nLoading data into SQLite...")

    connection = get_connection()

    load_dataframe(merged_df,          "fact_orders",         connection)
    load_dataframe(users_df,           "dim_users",           connection)
    load_dataframe(revenue_per_user,   "revenue_per_user",    connection)
    load_dataframe(revenue_by_country, "revenue_by_country",  connection)
    load_dataframe(daily_revenue,      "daily_revenue",       connection)

    connection.close()

    print(f"\n All tables loaded into: {DB_PATH}")


def verify_load():
    """
    Reads back all tables and confirms row counts.
    """
    print("\n Verifying loaded tables...")

    connection = get_connection()
    cursor = connection.cursor()

    tables = [
        "fact_orders",
        "dim_users",
        "revenue_per_user",
        "revenue_by_country",
        "daily_revenue"
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} rows")

    connection.close()


if __name__ == "__main__":
    import pandas as pd
    from scripts.extract import extract
    from scripts.transform import transform

    orders_df, users_df = extract()
    merged_df, revenue_per_user, revenue_by_country, daily_revenue = transform(
        orders_df, users_df
    )

    load(merged_df, users_df, revenue_per_user,
         revenue_by_country, daily_revenue)

    verify_load()