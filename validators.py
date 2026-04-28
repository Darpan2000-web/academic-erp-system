import re


def valid_password(password):
    # minimum 6 chars
    # one letter
    # one number
    # one symbol

    if len(password) < 6:
        return False

    if not re.search(r"[A-Za-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[^A-Za-z0-9]", password):
        return False

    return True


def valid_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email)


def valid_phone(phone):
    return phone.isdigit() and len(phone) == 10