import random
import time

# Store OTP temporarily
otp_store = {}


def generate_otp(username):
    """
    Create 6 digit OTP and save with timestamp
    """
    otp = str(random.randint(100000, 999999))

    otp_store[username] = {
        "otp": otp,
        "time": time.time()
    }

    return otp


def verify_otp(username, entered_otp, expiry_seconds=300):
    """
    Verify OTP
    expiry_seconds = 5 minutes default
    """

    if username not in otp_store:
        return False

    saved = otp_store[username]

    # Expired
    if time.time() - saved["time"] > expiry_seconds:
        otp_store.pop(username, None)
        return False

    # Correct OTP
    if saved["otp"] == entered_otp:
        otp_store.pop(username, None)
        return True

    return False


def clear_otp(username):
    otp_store.pop(username, None)