import os.path
import tornado.locale

tornado.locale.load_translations(os.path.abspath('.'))
print tornado.locale.get_supported_locales()

_ = tornado.locale.get('zh_CN').translate

print _('%s hours ago') % 1
