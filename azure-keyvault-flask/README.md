# (Python) Flaskの設定値のうち秘匿すべき設定値をAzure Key Vault上に保存しておき、Flask起動時に読み込むサンプル

[Azure Key Vault](https://docs.microsoft.com/ja-jp/azure/key-vault/)にはその名前の通り、秘匿したい情報を保持しアクセスコントロールするための[シークレット](https://docs.microsoft.com/ja-jp/azure/key-vault/secrets/)という機能がある。Flaskの設定値のうち秘匿すべき設定値（たとえばセッションを署名するのに使われる[`SECRET_KEY`](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)値など）をAzure Key Vaultのシークレットに保存しておき、Flask立ち上げ時にAzure Key Vaultから読み込んで設定するサンプル。

シークレットには25kbまでの値を保持できるので、このサンプルではJSON形式でFlaskの秘匿したい設定値を保持しておいている。具体的には次のような形のJSONを入れておき、Flask起動時にそれを読み込んで設定してる。

```
{
  "SECRET_KEY": "hoge",
  "OIDC_CLIENT_SECRET": "verySecret!"
}
```

FlaskからAzure Key Vaultにアクセスする際、Azure Identityライブラリ経由で資格情報を取得しアクセスすると次のことが実現できる。

* Azure Web Apps等にデプロイした際は、Web Appsに設定されてるManaged Identityの資格情報でアクセス
* ローカル開発環境上ではVisual Studio Codeの[Azure Account拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account)でログインした際の資格情報を使う。


# Azure Key Vaultを使う際の注意点

[Azure Key Vault サービスの制限](https://docs.microsoft.com/ja-jp/azure/key-vault/general/service-limits)に記載の通り、アクセス頻度に対して制限（スロットリング）がかけられているので注意。
具体的には、シークレットの場合、リージョンのコンテナごとに10秒間に最大2,000トランザクションまでと書かれている。[Azure Key Vault のスロットル ガイダンス](https://docs.microsoft.com/ja-jp/azure/key-vault/general/overview-throttling)にはこの制限に対するベストプラクティスが書かれている。

* 多数のシークレットを一度に読み取らない
* いったん読み取ったらメモリー上に乗せてキャッシュしておく
* Key Vaultにスロットリングされたら、Exponential Backoffでリトライする
* リージョン毎にスロットリングが適用されるため、必要に応じてAzure Key Vaultコンテナを複数のリージョンで使う

# 使ってるライブラリ

Poetryで管理してる。

* [azure-keyvault](https://pypi.org/project/azure-keyvault/) 4.1.0
* [azure-identity](https://pypi.org/project/azure-identity/) 1.5.0
* [flask](https://flask.palletsprojects.com/en/1.1.x/) 1.1.2
