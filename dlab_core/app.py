from flask import Flask

from dlab_core.plugins import APIPlugin

app = Flask(__name__)

app = APIPlugin.routes(app)


@app.route('/')
def health_check():
    return 'It works'


if __name__ == '__main__':
    app.run(debug=True)
