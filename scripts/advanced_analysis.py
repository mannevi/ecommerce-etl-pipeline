import sqlite3
from scripts.config import DB_PATH
from scripts.logger import get_logger

logger = get_logger("advanced_analysis")


def get_connection():
    return sqlite3.connect(DB_PATH)


def run_query(title, query):
    connection = get_connection()
    cursor = connection.cursor()

    print(f"\n{'='*55}")
    print(f"{title}")
    print(f"{'='*55}")

    cursor.execute(query)
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    print(" | ".join(columns))
    print("-" * 55)

    for row in rows:
        print(" | ".join(str(value) for value in row))

    connection.close()
    logger.info(f"Query ran: {title} — {len(rows)} rows returned")
    return rows


if __name__ == "__main__":

    # ── QUERY 1 ───────────────────────────────────────
    # CTE — Revenue summary then filter high value only
    # Business: Who are confirmed high value customers?
    run_query(
        "CTE — High Value Customers Only",
        """
        WITH revenue_summary AS (
            SELECT name,
                   SUM(amount) AS total_revenue
            FROM fact_orders
            GROUP BY name
        )
        SELECT name, total_revenue
        FROM revenue_summary
        WHERE total_revenue > 200
        ORDER BY total_revenue DESC
        """
    )

    # ── QUERY 2 ───────────────────────────────────────
    # CTE — Multi step: revenue then classify then filter
    # Business: Show only High Value and Mid Value customers
    run_query(
        "CTE — Customer Segments (Multi Step)",
        """
        WITH revenue_summary AS (
            SELECT name,
                   SUM(amount) AS total_revenue
            FROM fact_orders
            GROUP BY name
        ),
        segmented AS (
            SELECT name,
                   total_revenue,
                   CASE
                       WHEN total_revenue >= 500 THEN 'High Value'
                       WHEN total_revenue >= 200 THEN 'Mid Value'
                       ELSE 'Low Value'
                   END AS segment
            FROM revenue_summary
        )
        SELECT name, total_revenue, segment
        FROM segmented
        WHERE segment != 'Low Value'
        ORDER BY total_revenue DESC
        """
    )

    # ── QUERY 3 ───────────────────────────────────────
    # ROW_NUMBER — Rank customers within each country
    # Business: Who is the top spender in each country?
    run_query(
        "Window — Top Customer Per Country",
        """
        WITH revenue AS (
            SELECT name,
                   country,
                   SUM(amount) AS total_revenue
            FROM fact_orders
            GROUP BY name, country
        )
        SELECT name,
               country,
               total_revenue,
               ROW_NUMBER() OVER (
                   PARTITION BY country
                   ORDER BY total_revenue DESC
               ) AS rank_in_country
        FROM revenue
        ORDER BY country, rank_in_country
        """
    )

    # ── QUERY 4 ───────────────────────────────────────
    # SUM OVER — Running total revenue by date
    # Business: How is revenue accumulating over time?
    run_query(
        "Window — Running Total Revenue by Date",
        """
        SELECT order_date,
               SUM(amount) AS daily_revenue,
               SUM(SUM(amount)) OVER (
                   ORDER BY order_date
               ) AS running_total
        FROM fact_orders
        GROUP BY order_date
        ORDER BY order_date
        """
    )

    # ── QUERY 5 ───────────────────────────────────────
    # SUM OVER PARTITION — Each order's % of country total
    # Business: What share of country revenue does each order represent?
    run_query(
        "Window — Each Order Share of Country Revenue",
        """
        SELECT name,
               country,
               amount,
               SUM(amount) OVER (PARTITION BY country) AS country_total,
               ROUND(
                   amount * 100.0 /
                   SUM(amount) OVER (PARTITION BY country), 1
               ) AS pct_of_country
        FROM fact_orders
        ORDER BY country, amount DESC
        """
    )