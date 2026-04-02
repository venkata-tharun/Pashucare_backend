import pymysql
import pymysql.cursors
from config import DB_CONFIG


def get_connection():
    """Return a new PyMySQL connection using cursorclass=DictCursor."""
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        db=DB_CONFIG["db"],
        charset=DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor,
    )
