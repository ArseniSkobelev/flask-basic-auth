from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(import_name=__name__, template_folder=os.path.abspath('static/templates'), static_folder='static')
app.config.from_object(obj=Config)
db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
