# (Python) Azure ADから取得したアクセストークンを使いAzure SQL Databaseにpyodbcで接続するサンプル

[Azure SQL Database](https://azure.microsoft.com/ja-jp/products/azure-sql/database/)はSQL ServerのPaaS。そこに接続する際は、従来通りのID・Password認証（SQL 認証）も使えるが、Azure Active Directoryから取得出来るアクセストークンを使った認証でも接続できる。

Azure Identityライブラリを使いアクセストークンを取得しアクセスすると次のことが実現できる。

* Azure Web Apps等にデプロイした際は、Web Appsに設定されてるManaged Identityの資格情報でアクセス
* ローカル開発環境上ではVisual Studio Codeの[Azure Account拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account)でログインした際の資格情報を使う。


Azure ADのアクセストークンを使ってAzure SQL Databaseに接続するコードの例はpyodbcのWikiやSQLAlchemyのコードコメントに書かれてるので、それに従って実装している。
https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux#connecting
https://github.com/sqlalchemy/sqlalchemy/blob/rel_1_4_14/lib/sqlalchemy/dialects/mssql/pyodbc.py#L85-L140


# 使ってるライブラリ

Poetryで管理してる。

* [pyodbc](https://pypi.org/project/pyodbc/) 4.0.30
* [azure-identity](https://pypi.org/project/azure-identity/) 1.5.0
