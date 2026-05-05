import sqlite3
import os
from scripts.logger import get_logger

logger = get_logger("load")

DB_PATH = "data/ecommerce.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_dataframe(df, table_name, connection):
    df.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False
    )
    logger.info(f"Loaded {len(df)} rows into table: {table_name}")

def load(merged_df, users_df, revenue_per_user,
         revenue_by_country, daily_revenue):

    logger.info("Starting load...")
    connection = None

    try:
        connection = get_connection()

        load_dataframe(merged_df,          "fact_orders",        connection)
        load_dataframe(users_df,           "dim_users",          connection)
        load_dataframe(revenue_per_user,   "revenue_per_user",   connection)
        load_dataframe(revenue_by_country, "revenue_by_country", connection)
        load_dataframe(daily_revenue,      "daily_revenue",      connection)

        logger.info(f"All tables loaded into: {DB_PATH}")

    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise

    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed.")
def verify_load():
    logger.info("Verifying loaded tables...")
    connection = get_connection()
    cursor = connection.cursor()

    tables = [
        "fact_orders", "dim_users",
        "revenue_per_user", "revenue_by_country", "daily_revenue"
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        logger.info(f"{table}: {count} rows")

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