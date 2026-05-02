import pandas as pd

def extract():
    """
    Loads raw CSV files and returns two DataFrames.
    """
    print(" Extracting data...")

    orders_df = pd.read_csv("data/orders.csv")
    users_df = pd.read_csv("data/users.csv")

    print(f"Orders loaded: {len(orders_df)} rows")
    print(f"Users loaded: {len(users_df)} rows")

    return orders_df, users_df


if __name__ == "__main__":
    orders_df, users_df = extract()
    print(orders_df)
    print(users_df)