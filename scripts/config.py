import os

# ── Folder Paths ───────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
LOGS_DIR    = os.path.join(BASE_DIR, "logs")

# ── File Paths ─────────────────────────────────────
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
USERS_FILE  = os.path.join(DATA_DIR, "users.csv")
DB_PATH     = os.path.join(DATA_DIR, "ecommerce.db")

# ── Pipeline Settings ──────────────────────────────
CITIES = ["New York", "Chicago", "Houston", "Phoenix", "Cincinnati"]
MIN_ORDER_AMOUNT  = 0
START_DATE_FILTER = "2024-01-01"

# ── Customer Segments ──────────────────────────────
HIGH_VALUE_THRESHOLD = 500
MID_VALUE_THRESHOLD  = 200