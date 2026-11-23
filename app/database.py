
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_db():
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "parking_management"),
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False
    }

    if os.getenv("DB_SSL_VERIFY", "false").lower() == "true":
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True

        ca_path = os.getenv("DB_SSL_CA")
        if ca_path:
            config["ssl_ca"] = ca_path

    return pymysql.connect(**config)
