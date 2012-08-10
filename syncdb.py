from june.app import app, prepare_app

app.config.from_pyfile('_config/development.py')
prepare_app()

from june import account, node
account.models.db.create_all()
node.models.db.create_all()
