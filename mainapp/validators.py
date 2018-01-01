from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.six.moves.urllib.parse import urlsplit


class AmazonURLValidator(URLValidator):
    def __call__(self, value):
        super(AmazonURLValidator, self).__call__(value)
        netloc = urlsplit(value)[1]
        domain, tld = netloc.split('.')[-2:]
        if domain != 'amazon' or tld != 'com':
            raise ValidationError(self.message, code=self.code)
