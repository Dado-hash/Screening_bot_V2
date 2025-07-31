# Test configuration
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test database configuration
TEST_DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'screeningbot_test',
    'user': 'postgres',
    'password': 'dev_password',
    'port': 5432
}
