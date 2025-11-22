from django.core.validators import RegexValidator

# The '@' symbol is excluded.
# This makes sure usernames do not match email addresses.
username_validator = RegexValidator(
    r'^[\w.+-]+$',
    message=(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./+/-/_ characters.'
    ),
    code='invalid_username',
)
