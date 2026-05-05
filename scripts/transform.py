import pandas as pd
from scripts.logger import get_logger

logger = get_logger("transform")

def clean_orders(df):
    logger.info("Cleaning orders data...")
    median_amount = df["amount"].median()
    df["amount"] = df["amount"].fillna(median_amount)
    logger.info(f"Filled null amount with median: {median_amount}")
    df["order_date"] = pd.to_datetime(df["order_date"])
    logger.info("Converted order_date to datetime")
    df["amount"] = df["amount"].astype(int)
    df = df.drop_duplicates()
    logger.info(f"Orders cleaned: {len(df)} rows remaining")
    return df

def clean_users(df):
    logger.info("Cleaning users data...")
    df = df.drop_duplicates()
    df["country"] = df["country"].str.strip().str.title()
    df["name"] = df["name"].str.strip().str.title()
    logger.info(f"Users cleaned: {len(df)} rows remaining")
    return df

def filter_orders(df):
    logger.info("Filtering orders...")
    before = len(df)
    df = df[df["amount"] > 0]
    df = df[df["user_id"].notnull()]
    df = df[df["order_date"] >= "2024-01-01"]
    after = len(df)
    logger.info(f"Rows before filter: {before} → after: {after}")
    return df

def merge_data(orders_df, users_df):
    logger.info("Merging orders and users...")
    merged_df = pd.merge(orders_df, users_df, on="user_id", how="left")
    unmatched = merged_df["name"].isnull().sum()
    if unmatched > 0:
        logger.warning(f"{unmatched} orders have no matching user")
    else:
        logger.info("All orders matched to a user")
    logger.info(f"Merged dataset: {len(merged_df)} rows")
    return merged_df

def aggregate_data(merged_df):
    logger.info("Running aggregations...")

    revenue_per_user = merged_df.groupby("name")["amount"] \
        .sum().reset_index() \
        .rename(columns={"amount": "total_revenue"}) \
        .sort_values("total_revenue", ascending=False)

    revenue_by_country = merged_df.groupby("country")["amount"] \
        .sum().reset_index() \
        .rename(columns={"amount": "total_revenue"}) \
        .sort_values("total_revenue", ascending=False)

    daily_revenue = merged_df.groupby("order_date")["amount"] \
        .sum().reset_index() \
        .rename(columns={"amount": "daily_revenue"}) \
        .sort_values("order_date")

    logger.info(f"Revenue per user: {len(revenue_per_user)} users")
    logger.info(f"Revenue by country: {len(revenue_by_country)} countries")
    logger.info(f"Daily revenue: {len(daily_revenue)} days")

    return revenue_per_user, revenue_by_country, daily_revenue

def transform(orders_df, users_df):
    logger.info("Starting transformation...")

    try:
        orders_clean = clean_orders(orders_df)
        users_clean = clean_users(users_df)
        orders_filtered = filter_orders(orders_clean)
        merged_df = merge_data(orders_filtered, users_clean)
        revenue_per_user, revenue_by_country, daily_revenue = aggregate_data(merged_df)
        logger.info("Transformation complete.")
        return merged_df, revenue_per_user, revenue_by_country, daily_revenue

    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        raise