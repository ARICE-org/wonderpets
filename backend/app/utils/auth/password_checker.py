import re

error_message = []

def check_length(pw: str, min_len=8, max_len=16) -> bool:
    return min_len <= len(pw) <= max_len

def has_uppercase(pw: str) -> bool:
    return bool(re.search(r'[A-Z]', pw))

def has_lowercase(pw: str) -> bool:
    return bool(re.search(r'[a-z]', pw))

def has_digit(pw: str) -> bool:
    return bool(re.search(r'\d', pw))

def has_special(pw: str) -> bool:
    return bool(re.search(r'[^A-Za-z0-9]', pw))

def has_no_space(pw: str) -> bool:
    return not bool(re.search(r'\s', pw))

def is_valid_password(pw: str) -> bool:

    error_message.clear()
    if not check_length(pw):
         error_message.append("Length must be at least 8 characters, maximum is 16 characters")

    if not has_uppercase(pw):
        error_message.append("At least one uppercase character is required")

    if not has_lowercase(pw):
        error_message.append("At least one lowercase character is required")

    if not has_digit(pw):
        error_message.append("At least one digit is required")

    if not has_special(pw):
        error_message.append("At least one special character is required")

    if not has_no_space(pw):
        error_message.append("No space is required")

    if len(error_message) > 0:
        return False

    return True