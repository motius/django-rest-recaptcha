import json
import os

import requests

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .constants import GR_CAPTCHA_DEFAULT_URL, GR_CAPTCHA_TEST_SECRET_KEY


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

    def __init__(self, **kwargs):
        self.threshold = kwargs.pop('threshold', None)
        if self.threshold:
            assert isinstance(self.threshold, float) or isinstance(self.threshold, int), \
                   'threshold must be a number'
        super(ReCaptchaField, self).__init__(**kwargs)

    def to_representation(self, obj):
        self.fail('write_only')

    def to_internal_value(self, data):
        data = super(ReCaptchaField, self).to_internal_value(data)
        captcha_url = getattr(settings, 'GR_CAPTCHA_URL', GR_CAPTCHA_DEFAULT_URL)
        captcha_secret_key = getattr(settings, 'GR_CAPTCHA_SECRET_KEY', GR_CAPTCHA_TEST_SECRET_KEY)
        if os.environ.get('RECAPTCHA_TESTING', None) == 'True':
            return data

        res = requests.post(captcha_url, {
            'secret': captcha_secret_key,
            'response': data
        })
        return_values = json.loads(res.content.decode())
        return_code = return_values.get("success", False)
        score = return_values.get("score", 0.0)
        error_codes = return_values.get('error-codes', [])

        if self.threshold:
            if self.threshold <= score:
                return data
            else:
                self._raising_error_codes(error_codes=error_codes)

        if not return_code:
            self._raising_error_codes(error_codes=error_codes)
        return data

    def _raising_error_codes(self, error_codes):
        if error_codes and error_codes[0] in self.default_error_messages.keys():
            self.fail(error_codes[0])
        else:
            self.fail('bad-request')
