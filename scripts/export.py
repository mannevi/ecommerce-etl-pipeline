import sqlite3
import csv
import os
from datetime import datetime

from scripts.config import DB_PATH, OUTPUT_DIR

def get_connection():
    return sqlite3.connect(DB_PATH)


def export_to_csv(title, query, filename):
    """
    Runs a SQL query and saves results as a
    timestamped CSV file in the output folder.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{filename}_{timestamp}.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f" '{title}' saved to: {filepath}")
    connection.close()


if __name__ == "__main__":

    print(" Exporting reports...\n")

    # Report 1 — Top customers
    export_to_csv(
        "Top Customers",
        """
        SELECT name,
               SUM(amount) AS total_revenue
        FROM fact_orders
        GROUP BY name
        ORDER BY total_revenue DESC
        """,
        "top_customers"
    )

    # Report 2 — Revenue by country
    export_to_csv(
        "Revenue by Country",
        """
        SELECT country,
               SUM(amount)          AS total_revenue,
               COUNT(*)             AS total_orders,
               ROUND(AVG(amount),1) AS avg_order_value
        FROM fact_orders
        GROUP BY country
        ORDER BY total_revenue DESC
        """,
        "revenue_by_country"
    )

    # Report 3 — Daily revenue
    export_to_csv(
        "Daily Revenue",
        """
        SELECT order_date,
               SUM(amount) AS daily_revenue
        FROM fact_orders
        GROUP BY order_date
        ORDER BY order_date
        """,
        "daily_revenue"
    )

    # Report 4 — Customer segments
    export_to_csv(
        "Customer Segments",
        """
        SELECT name,
               SUM(amount) AS total_revenue,
               CASE
                   WHEN SUM(amount) >= 500 THEN 'High Value'
                   WHEN SUM(amount) >= 200 THEN 'Mid Value'
                   ELSE 'Low Value'
               END AS customer_segment
        FROM fact_orders
        GROUP BY name
        ORDER BY total_revenue DESC
        """,
        "customer_segments"
    )

    print("\nAll reports exported to output/ folder.")