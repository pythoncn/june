from june.handlers import front
from june.handlers import node
from june.handlers import topic
#from june.handlers import account
from june.handlers import api
from june import social

handlers = []
#handlers.extend(account.handlers)
handlers.extend(topic.handlers)
handlers.extend(node.handlers)
handlers.extend(api.handlers)
handlers.extend(social.handlers)
handlers.extend(front.handlers)

# mail test
from june.mail.handlers import handlers as mail_handlers
handlers.extend(mail_handlers)

sub_handlers = []
ui_modules = {}
ui_modules.update(topic.ui_modules)
ui_modules.update(node.ui_modules)
ui_modules.update(front.ui_modules)
#ui_modules.update(account.ui_modules)
