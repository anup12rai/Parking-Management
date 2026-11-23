
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db():
    ca_path = os.getenv("DB_SSL_CA", "database/isrgrootx1.pem")

    if not os.path.isabs(ca_path):
        ca_path = os.path.join(BASE_DIR, ca_path)

    if not os.path.isfile(ca_path):
        raise FileNotFoundError(f"TiDB CA certificate not found: {ca_path}")

    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "4000")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
        "connect_timeout": 15,
        "ssl_ca": ca_path,
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }

    return pymysql.connect(**config)
