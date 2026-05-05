import pandas as pd
from scripts.logger import get_logger

logger = get_logger("extract")

def extract():
    logger.info("Starting extraction...")

    try:
        orders_df = pd.read_csv("data/orders.csv")
        logger.info(f"Orders loaded: {len(orders_df)} rows")
    except FileNotFoundError:
        logger.error("orders.csv not found in data/ folder")
        raise

    try:
        users_df = pd.read_csv("data/users.csv")
        logger.info(f"Users loaded: {len(users_df)} rows")
    except FileNotFoundError:
        logger.error("users.csv not found in data/ folder")
        raise

    logger.info("Extraction complete.")
    return orders_df, users_df

if __name__ == "__main__":
    orders_df, users_df = extract()