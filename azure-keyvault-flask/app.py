from flask import Flask
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from logging import getLogger
from os import getenv
from azure.core.exceptions import ResourceNotFoundError
import json

logger = getLogger(__name__)

# Flaskの秘匿したい設定値JSONを保存したAzure Key Vaultのシークレットのキー
FLASK_SECRET_KEY = "flask-config"

"""
Azure Key Vaultシークレットには次のような形でFlaskの秘匿したい設定値を記入したJSONを入れておく。

{
  "SECRET_KEY": "hoge",
  "OIDC_CLIENT_SECRET": "verySecret!"
}
"""


def create_app(test_config=None):
    # 環境変数VAULT_URIにAzure Key VaultのコンテナURIを設定しておく
    VAULT_URI = getenv("VAULT_URI")
    if VAULT_URI is None:
        raise Exception("VAULT_URI env var is not set.")

    # Azure Identityを使い、Azure Key Vaultコンテナにアクセスする。
    # DefaultAzureCredentialを使うことで次のことが実現出来る。
    # ・Azure Web Apps等にデプロイした際は、Managed Identityの資格情報を使いKey Vaultにアクセス
    # ・ローカル開発環境上ではVisual StudioのAzure Account拡張機能でログインした際の資格情報を使いKey Vaultにアクセス
    credential = DefaultAzureCredential()
    valut_client = SecretClient(vault_url=VAULT_URI, credential=credential)

    # Azure Key Vaultコンテナ上に設定されているシークレットを読み出し、PythonのDictにする
    try:
        secret = valut_client.get_secret(FLASK_SECRET_KEY)
        flask_config = json.loads(secret.value)
    except ResourceNotFoundError as e:
        raise e
    except json.JSONDecodeError as e:
        raise e

    app = Flask(__name__, instance_relative_config=True)

    # シークレットから取得した値でconfigをアップデートする
    app.config.from_mapping(flask_config)

    @app.route("/")
    def hello_world():
        import datetime

        return "Hello from azure-keyvault-flask! " + str(datetime.datetime.now())

    return app
