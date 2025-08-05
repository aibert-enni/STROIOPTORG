from django.core.validators import RegexValidator

firstname_validator = RegexValidator(
    regex=r'^[A-Za-zА-Яа-яЁё\-]+$',
    message='Имя может содержать только буквы'
)

lastname_validator = RegexValidator(
    regex=r'^[A-Za-zА-Яа-яЁё\-]+$',
    message='Фамилия может содержать только буквы'
)

phone_number_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message='Номер телефона может содержать только цифры'
)

