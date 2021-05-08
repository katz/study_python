# (Python) SQLAlchemyとAlembicを使い、Azure SQL Databaseにトークン認証で接続しマイグレーションやDMLを実行するサンプル 

[Azure SQL Database](https://azure.microsoft.com/ja-jp/products/azure-sql/database/)はSQL ServerのPaaS。そこに接続する際は、従来通りのID・Password認証（SQL 認証）も使えるが、Azure Active Directoryから取得出来るアクセストークンを使った認証でも接続できる。

Azure Identityライブラリを使いアクセストークンを取得しAzure SQL Databaseアクセスすると次のことが実現できる。

* Azure Web Apps等にデプロイした際は、Web Appsに設定されてるManaged Identityの資格情報でAzure SQL Databaseへアクセス
* ローカル開発環境上ではVisual Studio Codeの[Azure Account拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account)でログインした際の資格情報を使いAzure SQL Databaseへアクセス。


[sqldb.py](sqldb.py)にSQLAlchemyでAzure SQL Databaseに接続する際にアクセストークンを使う際の実装を書いている。
Azure ADのアクセストークンを使ってAzure SQL Databaseに接続するコードの例はSQLAlchemyのコードコメントに書かれてるので、基本的にそれに従って実装している。
https://github.com/sqlalchemy/sqlalchemy/blob/rel_1_4_14/lib/sqlalchemy/dialects/mssql/pyodbc.py#L85-L140


Alembicのマイグレーション実行時にもアクセストークン認証を利用するため、 [alembic/env.py](alembic/env.py) に手を加えて sqldb.py で作ったengineを使うようにしてる。


おまけとして、ULIDをDBに永続化する際にVARCHAR(26)として永続化するための`TypeDecorator`実装が [`model/__init__.py`](model/__init__.py) に入っている。


# 使ってるライブラリ

Poetryで管理してる。

* [SQLAlchemy](https://pypi.org/project/sqlalchemy/) 1.4.14
* [Alembic](https://pypi.org/project/alembic/) 1.6.2
* [pyodbc](https://pypi.org/project/pyodbc/) 4.0.30
* [azure-identity](https://pypi.org/project/azure-identity/) 1.5.0
* [ulid-py](https://pypi.org/project/ulid-py/) 1.1.0

