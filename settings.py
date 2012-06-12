#debug = False
#address = '0.0.0.0'
sqlalchemy_engine = "mysql://user@localhost:3306/db?charset=utf8"
memcache = "127.0.0.1:11211"
cookie_secret = "secret"
password_secret = "secret"
static_url_prefix = '/static/'

sitename = "June"
siteurl = "http://127.0.0.1:8000"
#: if you have another sitefeed
#sitefeed = ""

#: google analytics
#ga = ""

#: register your recaptcha at www.google.com/recaptcha
#: this is a public key
recaptcha_key = '6Le9jtESAAAAAGBuFoL451V-0Vt-_xiNA8ACQiTd'
recaptcha_secret = '6Le9jtESAAAAAO2f24yTcAEnrnzUv35B1ofONIlR'

#: if you have a gravatar proxy
#gravatar_base_url = ''
#gravatar_extra = ''

emoji_url = 'http://python-china.b0.upaiyun.com/emojis/'

#twitter_key = ''
#twitter_secret = ''

image_backend = 'june.front.backends.LocalBackend'
local_static_path = '/tmp/'
local_static_url = 'http://path.to.com/'

#: upyun as image backend
#image_backend = 'june.front.backends.UpyunBackend'
#upyun_username = 'username'
#upyun_password = 'passowrd'
#upyun_bucket = 'bucket/directory'

#: smtp
smtp_user = 'noreply@gmail.com'
smtp_password = 'password'
smtp_host = 'smtp.gmail.com'
smtp_ssl = True
