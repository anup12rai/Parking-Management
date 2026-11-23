
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


def get_db():

    # Read database environment variables
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT", "4000"))
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "parking_management")

    # Read CA certificate path
    ca_path = os.getenv(
        "DB_SSL_CA",
        "database/tidb-ca.pem"
    )

    # Convert relative path to absolute path
    if not os.path.isabs(ca_path):
        ca_path = os.path.join(BASE_DIR, ca_path)

    # Diagnostic logs
    print("========== DATABASE DIAGNOSTICS ==========")
    print("PROJECT ROOT:", BASE_DIR)
    print("PROJECT ROOT EXISTS:", os.path.isdir(BASE_DIR))
    print("DATABASE HOST:", db_host)
    print("DATABASE PORT:", db_port)
    print("DATABASE NAME:", db_name)
    print("CA FILE PATH:", ca_path)

    database_folder = os.path.join(BASE_DIR, "database")

    print(
        "DATABASE FOLDER EXISTS:",
        os.path.isdir(database_folder)
    )

    if os.path.isdir(database_folder):
        print(
            "DATABASE FILES:",
            os.listdir(database_folder)
        )

    print(
        "CA FILE EXISTS:",
        os.path.isfile(ca_path)
    )

    print("==========================================")

    # Validate required environment variables
    if not all([db_host, db_user, db_password, db_name]):
        raise ValueError(
            "Missing database environment variables. "
            "Check Render Environment settings."
        )

    # Validate certificate
    if not os.path.isfile(ca_path):
        raise FileNotFoundError(
            f"TiDB CA certificate not found: {ca_path}"
        )

    # Database configuration
    config = {
        "host": db_host,
        "port": db_port,
        "user": db_user,
        "password": db_password,
        "database": db_name,
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
        "connect_timeout": 20,
        "read_timeout": 30,
        "write_timeout": 30,

        # TLS certificate verification
        "ssl_ca": ca_path,
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }

    # Connect to TiDB Cloud
    try:
        connection = pymysql.connect(**config)

        print("TiDB Cloud connection successful!")

        return connection

    except Exception as error:
        print("TiDB CONNECTION ERROR:", str(error))
        raise
