from scripts.extract import extract
from scripts.transform import transform
from scripts.load import load, verify_load
from scripts.export import export_to_csv, export_parquet
from scripts.quality_checks import run_all_checks
from scripts.logger import get_logger
from scripts.s3_upload import upload_all_reports, verify_s3_upload

logger = get_logger("pipeline")

def run_pipeline():
    logger.info("Starting E-commerce Pipeline...")

    try:
        # Step 1 — Extract
        orders_df, users_df = extract()

        # Step 2 — Transform
        merged_df, revenue_per_user, \
        revenue_by_country, daily_revenue = transform(orders_df, users_df)

        # Step 3 — Load
        load(merged_df, users_df, revenue_per_user,
             revenue_by_country, daily_revenue)
        verify_load()

        # Step 4 — Quality Checks
        checks_passed = run_all_checks()
        if not checks_passed:
            logger.error("Pipeline stopped — data quality checks failed")
            return

        # Step 5 — Export
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
           export_to_csv(
    "Customer Segments",
    "SELECT name, SUM(amount) AS total_revenue, CASE WHEN SUM(amount) >= 500 THEN 'High Value' WHEN SUM(amount) >= 200 THEN 'Mid Value' ELSE 'Low Value' END AS customer_segment FROM fact_orders GROUP BY name ORDER BY total_revenue DESC",
    "customer_segments"
)


        # Step 5b — Export Parquet (columnar format)
        from scripts.export import export_parquet
        export_parquet(merged_df, "orders_merged")
         # Step 5 — Upload to S3
        upload_all_reports()
        verify_s3_upload()

        logger.info(" Pipeline complete. Reports ready in output/ folder.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
