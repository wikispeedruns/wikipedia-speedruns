from flask_mail import Mail

mail = None

def init_app(app):
    global mail
    mail = Mail(app)

def get_mail():
    return mail

