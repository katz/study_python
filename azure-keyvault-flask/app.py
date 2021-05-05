from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    @app.route("/")
    def hello_world():
        import datetime

        return "Hello from azure-keyvault-flask! " + str(datetime.datetime.now())

    return app
