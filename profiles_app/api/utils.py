from django.core.exceptions import ValidationError


def validate_file_size(value):
    """
    Validates that the uploaded file size does not exceed the maximum limit (5 MB).
    """
    max_size = 5 * 1024 * 1024  # 5 MB in Byte
    if value.size > max_size:
        actual_size_mb = value.size / (1024 * 1024)
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            f"The uploaded file is too large: {actual_size_mb:.1f} MB. Maximum allowed size is {max_size_mb:.1f} MB."
        )
    return value
