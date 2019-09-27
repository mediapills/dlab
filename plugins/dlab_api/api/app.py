from flask import Flask

from api.notebooks.urls import notebook_bp
from api.projects.urls import project_bp
from api.templates.urls import template_bp

app = Flask(__name__)
app.register_blueprint(notebook_bp)
app.register_blueprint(project_bp)
app.register_blueprint(template_bp)


@app.route('/')
def health_check():
    return 'It works'


if __name__ == '__main__':
    app.run(debug=True)
