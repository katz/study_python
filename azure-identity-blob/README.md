# (Python) Flaskアプリで、Azure BlobへのアクセスにAzure Identityでの資格情報を使ってアクセスするサンプル

PythonからAzure Blobにアクセスする際、Azure Identityでの資格情報を使ってアクセスすると次のことが実現出来る。

* Azure Web Apps等にデプロイした際は、Web Appsに設定されてるManaged Identityの資格情報でアクセス
* ローカル開発環境上ではVisual Studio Codeの[Azure Account拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account)でログインした際の資格情報を使う。

こうすることで、環境変数にBlobにアクセスするためのConnection String等の資格情報をいちいち設定したり、その環境変数が漏れないように管理したり必要がなくなるのでとても便利。

## どうやってそんなことが実現出来てるの？

azure-identityライブラリの`DefaultAzureCredential`が以下のような順序でどの資格情報を使うか決めてくれるから。

1. 環境変数に設定された資格情報を参照する
1. AzureのManaged Identityの資格情報を参照する
1. （Windows限定） Visual StudioでAzureにログインした際の資格情報を参照する
1. Visual Studio CodeのAzure Account拡張機能でAzureにログインした際の資格情報を参照する。WindowsでもmacOSでもLinuxでも使える。
1. Azure CLIでAzureにログインした際の資格情報を参照する


# 使ってるライブラリ

Poetryで管理してる。

* [azure-storage-blob](https://pypi.org/project/azure-storage-blob/) 12.8.1
* [azure-identity](https://pypi.org/project/azure-identity/) 1.5.0
