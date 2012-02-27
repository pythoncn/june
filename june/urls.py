from june.handlers import front
from june.handlers import account
from june.handlers import dashboard

handlers = []
handlers.extend(account.handlers)
handlers.extend(dashboard.handlers)
handlers.extend(front.handlers)

sub_handlers = []
ui_modules = {}
