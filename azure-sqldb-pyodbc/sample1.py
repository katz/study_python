from azure import identity
import pprint
import pyodbc
import struct
from os import getenv
from logging import getLogger

logger = getLogger(__name__)

# Azure ADのトークンを使ってAzure SQL Databaseに接続するコードの例はSQLAlchemyのコードコメントに書かれてる
# https://github.com/sqlalchemy/sqlalchemy/blob/rel_1_4_14/lib/sqlalchemy/dialects/mssql/pyodbc.py#L85-L140


def get_access_token():
    """Azure ADからトークンを取得し、ODBC接続時に渡すAccessToken構造体に加工する

    ここで得られるトークンは数分で有効期限が切れるので、ODBCで接続を試みるたびに取得する必要がある点に注意。

    Returns:
       bytes: ODBC接続時に渡すAccessToken構造体
    """

    # Azure ADにトークンをリクエストする際、Azure SQL Databaseが操作できるようなトークンを取得するためのスコープ
    TOKEN_SCOPE = "https://database.windows.net//.default"

    cred = identity.DefaultAzureCredential()
    token = cred.get_token(TOKEN_SCOPE)

    """
    ODBCで渡すAccessToken構造体の定義は次の通りなので、このバイト構造に合わせるように加工する
    https://docs.microsoft.com/ja-jp/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver15#authenticating-with-an-access-token

    typedef struct AccessToken
    {
        DWORD dataSize;
        BYTE data[];
    } ACCESSTOKEN;
    """
    raw_token = token.token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(raw_token)}s", len(raw_token), raw_token)
    return token_struct


def get_connection(hostname, database, access_token):
    dsn = "DRIVER={driver};SERVER=tcp:{server};DATABASE={database};".format(
        driver="{ODBC Driver 17 for SQL Server}", server=hostname, database=database
    )

    # AccessToken構造体を渡すときの属性の番号。msodbcsql.hで定義されてる
    SQL_COPT_SS_ACCESS_TOKEN = 1256

    conn = pyodbc.connect(
        dsn,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: access_token},
    )

    return conn


hostname = getenv("SQLDB_HOST")
database = getenv("SQLDB_DBNAME")

if hostname is None or database is None:
    logger.error("環境変数 SQLDB_HOST と SQLDB_DBNAME を指定して下さい")
    exit()

# とりあえずSQL Databaseのバージョン取得してみる
conn = get_connection(hostname, database, get_access_token())
with conn:
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    for row in cursor.fetchall():
        pprint.pprint(row)
