from django.core.validators import RegexValidator

username_validator = RegexValidator(r'^[\w.+-]+$')
