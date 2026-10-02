from pymongo import MongoClient
from pymongo.collection import Collection
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

def load_env_file() -> None:
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "emafis")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
recommendations_collection: Collection = db["recommendations"]
portfolio_collection: Collection = db["portfolios"]
agent_performance_collection: Collection = db["agent_performance"]


def init_db():
    """Create useful indexes"""
    recommendations_collection.create_index([("ticker", 1), ("created_at", -1)])
    recommendations_collection.create_index([("evaluated", 1)])
    portfolio_collection.create_index("user_id", unique=True)
    print("✅ Database indexes ready")


def get_db():
    return db