import pandas as pd

def clean_orders(df):
   median_data=df["amount"].median()
   df["amount"]=df["amount"].fillna(median_data)
   df["order_date"]=pd.to_datetime(df["order_date"])
   df["amount"]=df["amount"].astype(int)
   df=df.drop_duplicates()
   return(df)
def clean_users(df):
   df=df.drop_duplicates()
   df["country"] = df["country"].str.strip().str.title()
   df["name"]=df["name"].str.strip().str.title()
   return df
def filter_orders(df):
   df=df[df["amount"]>0]
   df = df[df["user_id"].notnull()]
   df= df[df["order_date"] >= "2024-01-01"]
   return df
def merge_data(orders_df, users_df):
   merged_df = pd.merge(
        orders_df,
        users_df,
        on="user_id",
        how="left"
    )
   return merged_df
def aggregate_data(merged_df):
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

    return revenue_per_user, revenue_by_country, daily_revenue
def transform(orders_df, users_df):
    """
    Runs the full transform pipeline.
    Clean → Filter → Merge → Aggregate
    """
    print("\nTransforming data...")

    orders_clean = clean_orders(orders_df)
    users_clean = clean_users(users_df)
    orders_filtered = filter_orders(orders_clean)
    merged_df = merge_data(orders_filtered, users_clean)
    revenue_per_user, revenue_by_country, daily_revenue = aggregate_data(merged_df)

    print(f" Merged dataset: {len(merged_df)} rows")
    print(f" Revenue per user: {len(revenue_per_user)} users")
    print(f" Revenue by country: {len(revenue_by_country)} countries")
    print(f" Daily revenue: {len(daily_revenue)} days")

    return merged_df, revenue_per_user, revenue_by_country, daily_revenue


if __name__ == "__main__":
    orders_df = pd.read_csv("data/orders.csv")
    users_df = pd.read_csv("data/users.csv")
    transform(orders_df, users_df)