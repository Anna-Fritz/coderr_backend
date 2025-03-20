from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5 MB in Byte
    if value.size > max_size:
        raise ValidationError({'detail': 'Die Datei darf nicht größer als 5 MB sein.'})
    return value
