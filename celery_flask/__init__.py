import firebase_admin
import redis
from flask import Flask
from google.cloud import secretmanager

from .utils import celery_init_app, init_db

project_id = "flutter-app-demo-da31e"
app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        broker_url="pyamqp://guest@localhost//",
        result_backend="redis://localhost:6379/0",
        task_ignore_result=False,
        broker_connection_retry_on_startup=True,
        worker_concurrency=3,
        worker_prefetch_multiplier=1,
    ),
)

init_db(app)
celery = celery_init_app(app)
clientSecret = secretmanager.SecretManagerServiceClient()
default_app = firebase_admin.initialize_app()
redis_init = redis.Redis()


from .views import *
