from django.core.exceptions import ValidationError


def validate_file_size(value):
    """
    Validates that the uploaded file size does not exceed the maximum limit (5 MB).
    """
    max_size = 5 * 1024 * 1024  # 5 MB in Byte
    if value.size > max_size:
        raise ValidationError({'detail': 'Die Datei darf nicht größer als 5 MB sein.'})
    return value
