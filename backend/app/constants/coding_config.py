
from typing import List

FEATURE_KEYWORDS: List[str] = [
    'feature', 'functionality', 'requirement', 'capability', 'function'
]

DEFAULT_FEATURES: List[str] = [
    'User authentication', 
    'Data management', 
    'API endpoints', 
    'Database operations'
]

DEFAULT_ENV_CONFIG = {
    "DATABASE_URL": "sqlite:///./app.db",
    "SECRET_KEY": "your-secret-key-change-this-in-production",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30"
}
