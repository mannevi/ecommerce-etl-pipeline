import sqlite3
from scripts.config import DB_PATH
from scripts.logger import get_logger

logger = get_logger("quality_checks")


def get_connection():
    return sqlite3.connect(DB_PATH)


def check_nulls():
    """
    Checks that critical columns have no null values.
    In production — a null customer name means broken reporting.
    """
    logger.info("Running null check...")
    connection = get_connection()
    cursor = connection.cursor()

    checks = {
        "name":       "SELECT COUNT(*) FROM fact_orders WHERE name IS NULL",
        "amount":     "SELECT COUNT(*) FROM fact_orders WHERE amount IS NULL",
        "order_date": "SELECT COUNT(*) FROM fact_orders WHERE order_date IS NULL",
        "country":    "SELECT COUNT(*) FROM fact_orders WHERE country IS NULL",
    }

    passed = True
    for column, query in checks.items():
        cursor.execute(query)
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            logger.warning(f"Null check FAILED: {null_count} nulls in column '{column}'")
            passed = False
        else:
            logger.info(f"Null check PASSED: column '{column}'")

    connection.close()
    return passed


def check_row_count(min_rows=3):
    """
    Confirms at least min_rows exist in fact_orders.
    Catches silent empty loads.
    """
    logger.info("Running row count check...")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM fact_orders")
    count = cursor.fetchone()[0]
    connection.close()

    if count < min_rows:
        logger.warning(f"Row count check FAILED: {count} rows found, expected at least {min_rows}")
        return False

    logger.info(f"Row count check PASSED: {count} rows found")
    return True


def check_duplicates():
    """
    Confirms no duplicate order IDs exist.
    Duplicates cause revenue double counting.
    """
    logger.info("Running duplicate check...")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT order_id, COUNT(*) AS cnt
            FROM fact_orders
            GROUP BY order_id
            HAVING cnt > 1
        )
    """)
    duplicate_count = cursor.fetchone()[0]
    connection.close()

    if duplicate_count > 0:
        logger.warning(f"Duplicate check FAILED: {duplicate_count} duplicate order IDs found")
        return False

    logger.info("Duplicate check PASSED: no duplicate order IDs")
    return True


def check_range():
    """
    Confirms all order amounts are greater than zero.
    Negative amounts indicate refunds or data errors.
    """
    logger.info("Running range check...")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM fact_orders WHERE amount <= 0")
    invalid_count = cursor.fetchone()[0]
    connection.close()

    if invalid_count > 0:
        logger.warning(f"Range check FAILED: {invalid_count} orders with amount <= 0")
        return False

    logger.info("Range check PASSED: all amounts are valid")
    return True


def check_schema():
    """
    Confirms all expected columns exist in fact_orders.
    Catches upstream pipeline breaks that drop columns.
    """
    logger.info("Running schema check...")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(fact_orders)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    connection.close()

    expected_columns = [
        "order_id", "user_id", "amount",
        "order_date", "name", "country"
    ]

    passed = True
    for col in expected_columns:
        if col not in existing_columns:
            logger.warning(f"Schema check FAILED: column '{col}' missing")
            passed = False
        else:
            logger.info(f"Schema check PASSED: column '{col}' exists")

    return passed


def run_all_checks():
    """
    Runs all quality checks and returns overall pass/fail.
    This is your data quality gate.
    """
    logger.info("=" * 50)
    logger.info("Starting data quality checks...")
    logger.info("=" * 50)

    results = {
        "null_check":      check_nulls(),
        "row_count_check": check_row_count(),
        "duplicate_check": check_duplicates(),
        "range_check":     check_range(),
        "schema_check":    check_schema(),
    }

    logger.info("=" * 50)
    logger.info("Data Quality Summary:")
    all_passed = True
    for check, passed in results.items():
        status = "PASSED" if passed else " FAILED"
        logger.info(f"  {check}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        logger.info("Overall:  ALL CHECKS PASSED — data is ready")
    else:
        logger.warning("Overall:  SOME CHECKS FAILED — review logs")

    logger.info("=" * 50)
    return all_passed


if __name__ == "__main__":
    run_all_checks()