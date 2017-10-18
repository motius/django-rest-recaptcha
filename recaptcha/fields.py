import json
import requests

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .constants import GR_CAPTCHA_TEST_SECRET_KEY, GR_CAPTCHA_DEFAULT_URL


class ReCaptchaField(serializers.CharField):
    extra_error_messages = {
        'write_only': _('This is a write only field'),
        'missing-input-secret': _('Secret key is missing. Please contact admin.'),
        'invalid-input-secret': _('The secret key is invalid or malformed.'),
        'missing-input-response': _('Please check the checkbox to prove you are not a robot.'),
        'invalid-input-response': _('The response is invalid or malformed.'),
        'bad-request': _('Bad request.'),
        'timeout-or-duplicate': _('Verification has timed out or duplicate.')
    }
    default_error_messages = serializers.CharField.default_error_messages.copy()
    default_error_messages.update(extra_error_messages)

    def to_representation(self, obj):
        self.fail('write_only')

    def to_internal_value(self, data):
        data = super(ReCaptchaField, self).to_internal_value(data)
        captcha_url = getattr(settings, 'GR_CAPTCHA_URL', GR_CAPTCHA_DEFAULT_URL)
        captcha_secret_key = getattr(settings, 'GR_CAPTCHA_SECRET_KEY', GR_CAPTCHA_TEST_SECRET_KEY)
        res = requests.post(captcha_url, {
            'secret': captcha_secret_key,
            'response': data
        })
        return_values = json.loads(res.content.decode())
        return_code = return_values.get("success", False)
        error_codes = return_values.get('error-codes', [])
        if not return_code:
            if error_codes and error_codes[0] in self.default_error_messages.keys():
                self.fail(error_codes[0])
            else:
                self.fail('bad-request')
        return data
