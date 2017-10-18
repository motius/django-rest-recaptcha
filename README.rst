Django Rest reCAPTCHA
================
**Django Rest reCAPTCHA field to add google recaptcha in django-rest-framework**


Requirements
------------

Tested with:

* Python: 2.7, 3.5
* Django: 1.8, 1.9, 1.10, 1.11

Installation
------------

#. Install with ``pip install django-rest-recaptcha``.

#. Add ``'recaptcha'`` to your ``INSTALLED_APPS`` setting.

#. Register and obtain recaptcha keys here `https://www.google.com/recaptcha/admin`

#. Add the obtained keys to settings(For testing and development you can leave it blank to use
default test keys as mentioned here `https://developers.google.com/recaptcha/docs/faq`).
For example:

   .. code-block:: python

       GR_CAPTCHA_SECRET_KEY = 'GoogleRecaptchaPrivateKey001'

Usage
-----

#. Now you can import and use the recaptcha field in your serializer.
For example:

   .. code-block:: python

       from rest_framework import serializers
       from recaptcha.fields import ReCaptchaField

       class ExampleSerializer(serializers.Serializer):
            recaptcha = ReCaptchaField(write_only=True)
            ...
