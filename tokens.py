from itsdangerous import URLSafeTimedSerializer

ts = None

def init_app(app):
    global ts
    ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

