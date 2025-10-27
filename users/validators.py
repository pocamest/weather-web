from django.core.validators import RegexValidator

username_validator = RegexValidator(
    r'^[\w.+-]+$',
    message=(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./+/-/_ characters.'
    ),
)
