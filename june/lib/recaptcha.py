import logging
import urllib

from tornado.auth import httpclient
from tornado.options import options


class RecaptchaMixin(object):
    RECAPTCHA_VERIFY_URL = "http://www.google.com/recaptcha/api/verify"

    def recaptcha_render(self):
        token = self._recaptcha_token()
        html = ('<div id="recaptcha_div"></div><script type="text/javascript" '
                'src="http://www.google.com/recaptcha/api/js/recaptcha_ajax.js'
                '"></script><script type="text/javascript">Recaptcha.create'
                '("%(key)s", "recaptcha_div", {theme: "%(theme)s",callback:'
                'Recaptcha.focus_response_field});</script>')
        return html % token

    def recaptcha_validate(self, callback):
        token = self._recaptcha_token()
        challenge = self.get_argument('recaptcha_challenge_field', None)
        response = self.get_argument('recaptcha_response_field', None)
        callback = self.async_callback(self._on_recaptcha_request, callback)
        http = httpclient.AsyncHTTPClient()
        post_args = {
            'privatekey': token['secret'],
            'remoteip': self.request.remote_ip,
            'challenge': challenge,
            'response': response
        }
        http.fetch(self.RECAPTCHA_VERIFY_URL, method="POST",
                   body=urllib.urlencode(post_args), callback=callback)

    def _on_recaptcha_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                    response.request.url)
            callback(None)
            return
        verify, message = response.body.split()
        if verify == 'true':
            callback(response.body)
        else:
            logging.warning("Recaptcha verify failed %s", message)
            callback(None)

    def _recaptcha_token(self):
        token = dict(
            key=options.recaptcha_key,
            secret=options.recaptcha_secret,
            theme=options.recaptcha_theme,
        )
        return token
