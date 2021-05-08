import struct
import urllib
from os import getenv
from azure import identity
from sqlalchemy import create_engine
from sqlalchemy.event import listens_for
from logging import getLogger

logger = getLogger(__name__)


def _get_access_token():
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


def get_connection_url():
    """環境変数 SQLDB_HOST と SQLDB_DBNAME から、SQLAlchemyのcreate_engine()に渡すURLを構築する"""
    hostname = getenv("SQLDB_HOST")
    database = getenv("SQLDB_DBNAME")

    if hostname is None or database is None:
        logger.error("環境変数 SQLDB_HOST と SQLDB_DBNAME を指定して下さい")
        exit()
    pass

    dsn = "DRIVER={driver};SERVER=tcp:{server};DATABASE={database};".format(
        driver="{ODBC Driver 17 for SQL Server}", server=hostname, database=database
    )

    return "mssql+pyodbc:///?odbc_connect={}".format(urllib.parse.quote_plus(dsn))


def get_engine(poolclass=None):
    engine = create_engine(get_connection_url(), poolclass=poolclass)

    # SQLAlchemyがAzure SQL Databaseに接続する際、
    # Azure Active Directoryから取得したアクセストークンを渡して認証するようにする
    @listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):
        # SQLAlchemyは接続文字列に「Trusted_Connection」を付与するが、それがあるとアクセストークン認証がエラーになるので取り除く
        # https://docs.microsoft.com/ja-jp/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver15#new-andor-modified-connection-attributes
        cargs[0] = cargs[0].replace(";Trusted_Connection=Yes", "")

        # AccessToken構造体を渡すときの属性の番号。msodbcsql.hで定義されてる
        SQL_COPT_SS_ACCESS_TOKEN = 1256

        # apply it to keyword arguments
        cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: _get_access_token()}

    return engine
