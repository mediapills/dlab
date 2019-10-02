from flask import Flask

from api.processes_manager import Manager
from dlab_core.plugins import APIPlugin

app = Flask(__name__)

app = APIPlugin.routes(app)
app.manager = Manager()


@app.route('/')
def health_check():
    return 'It works'


if __name__ == '__main__':
    app.run(debug=False)  # pragma: nocover
