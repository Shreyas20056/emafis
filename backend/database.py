from pymongo import MongoClient
from pymongo.collection import Collection
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

def load_env_file() -> None:
    env_path = BACKEND_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

MONGO_URI = os.getenv("MONGO_URL") or os.getenv("MONGO_URI") or "mongodb://localhost:27017/emafis"
DB_NAME = os.getenv("MONGO_DB_NAME", "emafis")

# Parse default database from URL if present
if "://" in MONGO_URI and "/" in MONGO_URI.split("://")[-1]:
    uri_db = MONGO_URI.split("://")[-1].split("/")[1].split("?")[0]
    if uri_db:
        DB_NAME = uri_db

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[DB_NAME]

# Collections
recommendations_collection: Collection = db["recommendations"]
portfolio_collection: Collection = db["portfolios"]
agent_performance_collection: Collection = db["agent_performance"]
users_collection: Collection = db["users"]


def init_db():
    """Create useful indexes safely and seed initial data"""
    try:
        recommendations_collection.create_index([("ticker", 1), ("created_at", -1)])
        recommendations_collection.create_index([("evaluated", 1)])
        portfolio_collection.create_index("user_id", unique=True)
        users_collection.create_index("email", unique=True)
        agent_performance_collection.create_index("agent", unique=True)
        print("[OK] Database connected & indexes ready")

        # Initialize agent performance collection in MongoDB
        from core.learning import init_agent_performance
        init_agent_performance()
    except Exception as e:
        print(f"[WARN] Could not initialize DB (MongoDB offline?): {e}")




def get_db():
    return db
