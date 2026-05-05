import pandas as pd
from scripts.logger import get_logger

logger = get_logger("extract")

def extract():
    """
    Loads raw CSV files and returns two DataFrames.
    """
    logger.info("Starting extraction...")

    try:
        orders_df = pd.read_csv("data/orders.csv")
        logger.info(f"Orders loaded: {len(orders_df)} rows")

        users_df = pd.read_csv("data/users.csv")
        logger.info(f"Users loaded: {len(users_df)} rows")

        logger.info("Extraction complete.")
        return orders_df, users_df

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise

if __name__ == "__main__":
    orders_df, users_df = extract()