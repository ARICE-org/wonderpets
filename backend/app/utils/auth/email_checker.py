import re

error_message = []

def has_at_symbol(email: str) -> bool:
    return "@" in email

def valid_username(email: str) -> bool:
    if "@" not in email:
        return False
    username = email.split("@")[0]
    # Must only contain allowed chars and not start with . or -
    return bool(re.fullmatch(r"[A-Za-z0-9._-]+", username)) and not username.startswith((".", "-"))

def valid_domain(email: str) -> bool:
    if "@" not in email:
        return False
    domain = email.split("@")[1]
    # Must contain at least one dot
    if "." not in domain:
        return False
    # Valid domain format: no starting -, valid TLD
    return bool(re.fullmatch(r"(?!-)([A-Za-z0-9-]+\.)+[A-Za-z]{2,}", domain))

def has_no_spaces(email: str) -> bool:
    return " " not in email

def is_valid_email(email: str) -> bool:
    error_message.clear()

    if not has_at_symbol(email):
        error_message.append("Email must contain '@' symbol")

    if not valid_username(email):
        error_message.append("Invalid username (before '@')")

    if not valid_domain(email):
        error_message.append("Invalid domain (after '@')")

    if not has_no_spaces(email):
        error_message.append("Email must not contain spaces")

    if len(error_message) > 0:
        return False

    return True