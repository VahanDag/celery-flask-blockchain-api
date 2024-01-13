import datetime
import json
import sqlite3
import traceback

from celery import Celery, Task
from flask import Flask, request


def init_db(app: Flask):
    with app.app_context():
        db = sqlite3.connect('app.db')
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_logs (
            timestamp TEXT,
            task_id TEXT,
            status TEXT,
            args TEXT,
            kwargs TEXT,
            result TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS flask_errors (
            timestamp TEXT,
            request_data TEXT,
            error_message TEXT
        )
        ''')
        db.commit()
        db.close()

def log_flask_error(error):
    error_message = str(error)
    timestamp = datetime.datetime.now().isoformat()
    request_data = request.get_json(silent=True) or {}

    with open('flask_errors.log', 'a') as file:
        file.write(f"{timestamp}: ERROR - Request Data: {request_data} - Error: {error_message}\n")

    db = sqlite3.connect('app.db')
    cursor = db.cursor()
    cursor.execute('INSERT INTO flask_errors (timestamp, request_data, error_message) VALUES (?, ?, ?)',
                   (timestamp, json.dumps(request_data), error_message))
    db.commit()
    db.close()
    


def insert_log(timestamp, task_id, status, args, kwargs, result):
    db = sqlite3.connect('app.db')
    cursor = db.cursor()
    cursor.execute('INSERT INTO task_logs (timestamp, task_id, status, args, kwargs, result) VALUES (?, ?, ?, ?, ?, ?)',
                   (timestamp, task_id, status, str(args), str(kwargs), str(result)))
    db.commit()
    db.close()

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        # Flask uygulama bağlamını koruyan __call__ metodu
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

        # Görev başarılı olduğunda çağrılan metod
        def on_success(self, retval, task_id, args, kwargs):
            insert_log(datetime.datetime.now(), task_id, 'SUCCESS', args, kwargs, retval)
            with open('task_results_success.log', 'a') as file:
                file.write(f"{datetime.datetime.now()}: SUCCESS - Task ID: {task_id}, Args: {args}, Kwargs: {kwargs}, Return Value: {retval}\n")

        # Görev başarısız olduğunda çağrılan metod
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            insert_log(datetime.datetime.now(), task_id, 'FAILURE', args, kwargs, str(exc))
            with open('task_results_failure.log', 'a') as file:
                file.write(f"{datetime.datetime.now()}: FAILURE - Task ID: {task_id}, Args: {args}, Kwargs: {kwargs}, Exception: {exc}\n")

    # Celery uygulamasını başlatma ve yapılandırma
    celery_app = Celery(app.name)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.Task = FlaskTask
    
    return celery_app

