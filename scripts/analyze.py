import sqlite3

DB_PATH = "data/ecommerce.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def run_query(title, query):
    """
    Runs a SQL query and prints results cleanly.
    """
    connection = get_connection()
    cursor = connection.cursor()

    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

    cursor.execute(query)
    rows = cursor.fetchall()

    # Print column headers
    columns = [desc[0] for desc in cursor.description]
    print(" | ".join(columns))
    print("-" * 50)

    # Print each row
    for row in rows:
        print(" | ".join(str(value) for value in row))

    connection.close()
    return rows


if __name__ == "__main__":

    # ── QUERY 1 ──────────────────────────────────────
    # Who are the top customers by total spend?
    run_query(
        "Top Customers by Revenue",
        """
        SELECT name,
               SUM(amount) AS total_revenue
        FROM fact_orders
        GROUP BY name
        ORDER BY total_revenue DESC
        """
    )

    # ── QUERY 2 ──────────────────────────────────────
    # Which country generates the most revenue?
    run_query(
        "Revenue by Country",
        """
        SELECT country,
               SUM(amount)   AS total_revenue,
               COUNT(*)      AS total_orders,
               ROUND(AVG(amount), 1) AS avg_order_value
        FROM fact_orders
        GROUP BY country
        ORDER BY total_revenue DESC
        """
    )

    # ── QUERY 3 ──────────────────────────────────────
    # What is the daily revenue trend?
    run_query(
        "Daily Revenue Trend",
        """
        SELECT order_date,
               SUM(amount) AS daily_revenue
        FROM fact_orders
        GROUP BY order_date
        ORDER BY order_date
        """
    )

    # ── QUERY 4 ──────────────────────────────────────
    # What percentage of total revenue does each user contribute?
    run_query(
        "Each Customer Revenue Share %",
        """
        SELECT name,
               SUM(amount) AS total_revenue,
               ROUND(
                   SUM(amount) * 100.0 /
                   (SELECT SUM(amount) FROM fact_orders), 1
               ) AS revenue_share_pct
        FROM fact_orders
        GROUP BY name
        ORDER BY total_revenue DESC
        """
    )

    # ── QUERY 5 ──────────────────────────────────────
    # Classify each customer by their spend level
    run_query(
        "Customer Spend Classification",
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
        """
    )