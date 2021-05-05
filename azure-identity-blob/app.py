import os
from azure.storage.blob import BlobServiceClient, ExponentialRetry
from azure.identity import DefaultAzureCredential
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/containers", methods=["GET"])
def list_blobs():
    # 接続先BlobアカウントのURL作る
    blob_url = "https://{}.blob.core.windows.net".format(
        os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    )

    # DefaultAzureCredentialを使い、Blobに接続するためのCredentialを自動で取得する。
    # DefaultAzureCredentialを使うと、次の順番でCredentialの取得を試みる。
    # なので、Azure上ではManaged IDの資格情報、ローカル開発環境上ではVSCodeの資格情報が使われるといったことが自動的に行われる。
    #  1. EnvironmentCredential
    #     環境変数に設定されてるCredentialを使う
    #     https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python
    #  2. ManagedIdentityCredential
    #     AzureのManaged Identityを使う
    #     https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python
    #  3. SharedTokenCacheCredential
    #     WindowsのVisual Studio等でログインした際のCredentialを使う
    #     https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.sharedtokencachecredential?view=azure-python
    #  4. VisualStudioCodeCredential
    #     Visual Studio CodeのAzure Account拡張機能でログインした際のCredentialを使う。
    #     Windows、macOS、Linux対応。
    #     https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account
    #     https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.visualstudiocodecredential?view=azure-python
    #  5. AzureCliCredential
    #     AzureのCLIでログインした際のCredentialを使う。
    #     https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.azureclicredential?view=azure-python
    cred = DefaultAzureCredential()

    # Blobに接続する際、パラメータを明示したExponentialRetryを使う。
    # デフォルトだとExponentialRetryが使われるがその際のデフォルトパラメータは
    #   initial_backoff=15, increment_base=3, retry_total=3, random_jitter_range=3
    #
    # なので、リトライ分含め合計4回接続を試み、リトライの間隔は
    #   (15+3^1) = 18±3秒、(15+3^2) = 24±3秒、(15+3^3) = 42±3秒
    # になるので、Flaskに接続してくるclientのHTTP Connectionを長時間保持したままになってしまう。
    #
    # それがイヤだったら明示的にパラメータを設定して早めにBlobに対してリトライをかける。
    # このコードの例だと、
    #   (0.5+1.2^1) = 1.7±0.2秒、(0.5+1.2^2) = 1.94±0.2秒、(0.5+1.2^3) = 2.228±0.2秒
    # の間隔でのリトライになる。
    retry = ExponentialRetry(
        initial_backoff=0.5, increment_base=1.2, random_jitter_range=0.2
    )
    client = BlobServiceClient(blob_url, cred, retry_policy=retry)
    containers = client.list_containers()
    container_names = [container.get("name", "unknown") for container in containers]

    return ", ".join(container_names)
