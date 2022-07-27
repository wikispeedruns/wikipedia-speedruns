from celery import Celery
import json

# load settings for celery broker from prod.json
try:
    config = json.load(open('config/prod.json'))
    celery = Celery(__name__,
        broker=config.get("CELERY_BROKER_URL"),
        backend=config.get("CELERY_RESULT_BACKEND")
    )
except FileNotFoundError:
    # Otherwise just open a celery connection that points nowhere
    celery = Celery(__name__)


def make_celery(app):

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

