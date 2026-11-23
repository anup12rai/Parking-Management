
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_db():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "parking_management"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

    return connection
