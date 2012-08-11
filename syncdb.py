from june.app import app, prepare_app

app.config.from_pyfile('_config/development.py')
prepare_app()

from june.database import db
db.create_all()
