import pandas as pd
from scripts.logger import get_logger
from scripts.config import ORDERS_FILE, USERS_FILE

logger = get_logger("extract")

def extract():
    logger.info("Starting extraction...")

    try:
        orders_df = pd.read_csv(ORDERS_FILE)
        logger.info(f"Orders loaded: {len(orders_df)} rows")
    except FileNotFoundError:
        logger.error(f"File not found: {ORDERS_FILE}")
        raise

    try:
        users_df = pd.read_csv(USERS_FILE)
        logger.info(f"Users loaded: {len(users_df)} rows")
    except FileNotFoundError:
        logger.error(f"File not found: {USERS_FILE}")
        raise

    logger.info("Extraction complete.")
    return orders_df, users_df

if __name__ == "__main__":
    orders_df, users_df = extract()