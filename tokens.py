from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired

ts = None

def init_app(app):
    global ts
    ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Use hash for salt, so this signature is invalid when password is changed
def create_reset_token(id, hash):
    return ts.dumps(id, salt="reset-" + hash)

def verify_reset_token(token, hash):
    try:
        return ts.loads(token, max_age=86400, salt="reset-" + hash)
    except (SignatureExpired, BadSignature) as e:
        return None

def create_confirm_token(id):
    return ts.dumps(id, salt="confirm-email")

def verify_confirm_token(token):
    try:
        return ts.loads(token, max_age=3600, salt="confirm-email")
    except (SignatureExpired, BadSignature):
        return None