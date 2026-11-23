
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
        "autocommit": False,
        "connect_timeout": 15,
    }

    # Enable secure TLS for TiDB Cloud
    if os.getenv("DB_SSL_VERIFY", "false").lower() == "true":
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True
        config["ssl_ca"] = os.getenv(
            "DB_SSL_CA",
            "/etc/ssl/certs/ca-certificates.crt"
        )

    return pymysql.connect(**config)
