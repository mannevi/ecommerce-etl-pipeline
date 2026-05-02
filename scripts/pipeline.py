from scripts.extract import extract
from scripts.transform import transform
from scripts.load import load, verify_load
from scripts.export import export_to_csv

def run_pipeline():
    print("Starting E-commerce Pipeline...\n")

    # Step 1 — Extract
    orders_df, users_df = extract()

    # Step 2 — Transform
    merged_df, revenue_per_user, \
    revenue_by_country, daily_revenue = transform(orders_df, users_df)

    # Step 3 — Load
    load(merged_df, users_df, revenue_per_user,
         revenue_by_country, daily_revenue)
    verify_load()

    # Step 4 — Export
    print("\n Exporting reports...")

    export_to_csv(
        "Top Customers",
        "SELECT name, SUM(amount) AS total_revenue FROM fact_orders GROUP BY name ORDER BY total_revenue DESC",
        "top_customers"
    )
    export_to_csv(
        "Revenue by Country",
        "SELECT country, SUM(amount) AS total_revenue FROM fact_orders GROUP BY country ORDER BY total_revenue DESC",
        "revenue_by_country"
    )
    export_to_csv(
        "Daily Revenue",
        "SELECT order_date, SUM(amount) AS daily_revenue FROM fact_orders GROUP BY order_date ORDER BY order_date",
        "daily_revenue"
    )

    print("\n Pipeline complete. Reports ready in output/ folder.")


if __name__ == "__main__":
    run_pipeline()