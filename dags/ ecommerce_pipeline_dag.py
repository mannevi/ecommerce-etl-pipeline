from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from scripts.extract import extract
from scripts.transform import transform
from scripts.load import load, verify_load
from scripts.quality_checks import run_all_checks
from scripts.export import export_to_csv, export_parquet
from scripts.s3_upload import upload_all_reports, verify_s3_upload
from scripts.logger import get_logger

logger = get_logger("ecommerce_dag")

default_args = {
    "owner": "manne_vaishnavi",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def run_extract(**context):
    orders_df, users_df = extract()
    context["ti"].xcom_push(key="orders_df", value=orders_df.to_json())
    context["ti"].xcom_push(key="users_df", value=users_df.to_json())


def run_transform(**context):
    import pandas as pd
    orders_df = pd.read_json(context["ti"].xcom_pull(key="orders_df"))
    users_df  = pd.read_json(context["ti"].xcom_pull(key="users_df"))
    merged_df, revenue_per_user, revenue_by_country, daily_revenue = transform(
        orders_df, users_df
    )
    context["ti"].xcom_push(key="merged_df",          value=merged_df.to_json())
    context["ti"].xcom_push(key="revenue_per_user",   value=revenue_per_user.to_json())
    context["ti"].xcom_push(key="revenue_by_country", value=revenue_by_country.to_json())
    context["ti"].xcom_push(key="daily_revenue",      value=daily_revenue.to_json())


def run_load(**context):
    import pandas as pd
    merged_df          = pd.read_json(context["ti"].xcom_pull(key="merged_df"))
    revenue_per_user   = pd.read_json(context["ti"].xcom_pull(key="revenue_per_user"))
    revenue_by_country = pd.read_json(context["ti"].xcom_pull(key="revenue_by_country"))
    daily_revenue      = pd.read_json(context["ti"].xcom_pull(key="daily_revenue"))
    from scripts.extract import extract
    _, users_df = extract()
    load(merged_df, users_df, revenue_per_user, revenue_by_country, daily_revenue)
    verify_load()


def run_quality_checks(**context):
    passed = run_all_checks()
    if not passed:
        raise Exception("Data quality checks failed — pipeline stopped.")


def run_export(**context):
    import pandas as pd
    merged_df = pd.read_json(context["ti"].xcom_pull(key="merged_df"))
    export_to_csv(
        "Top Customers",
        "SELECT name, SUM(amount) AS total_revenue FROM fact_orders GROUP BY name ORDER BY total_revenue DESC",
        "top_customers"
    )
    export_to_csv(
        "Revenue by Country",
        "SELECT country, SUM(amount) AS total_revenue, COUNT(*) AS total_orders, ROUND(AVG(amount),1) AS avg_order_value FROM fact_orders GROUP BY country ORDER BY total_revenue DESC",
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
    export_parquet(merged_df, "orders_merged")
    upload_all_reports()
    verify_s3_upload()


with DAG(
    dag_id="ecommerce_etl_pipeline",
    default_args=default_args,
    description="End-to-end E-Commerce ETL Pipeline",
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "ecommerce", "sqlite", "s3"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=run_extract,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=run_transform,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=run_load,
    )

    quality_task = PythonOperator(
        task_id="quality_checks",
        python_callable=run_quality_checks,
    )

    export_task = PythonOperator(
        task_id="export_and_upload",
        python_callable=run_export,
    )

    # Pipeline order
    extract_task >> transform_task >> load_task >> quality_task >> export_task
