from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _


class CustomMinValidator(BaseValidator):
    message = _('Минимум %(limit_value)s.')
    code = 'min_value'

    def compare(self, a, b):
        return a < b
