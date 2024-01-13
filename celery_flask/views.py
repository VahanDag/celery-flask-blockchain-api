import datetime
import json
import sqlite3

from firebase_admin import auth
from flask import jsonify, request

from celery_flask import app
from celery_flask.tasks import admin_action

from .address_settings import get_address_private_nonce, get_next_admin_index
from .utils import log_flask_error

function_list = ["updateFactorX", "levelUp", "mintReward", "changeInitialPrice"]



############### FLASK ###############
@app.route('/api/adminAction', methods=['POST'])
def admin_action_endpoint():
    data = request.get_json()
    token = request.headers.get('Authorization')

    if not token:
        return jsonify(message = 'Authorization token is missing'), 401
    
    try:
        token = token.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
    except Exception as e:
        log_flask_error(e)
        return jsonify(message="You are not allowed"), 500
        # return jsonify(message = "error: {}".format(e)), 403
        
    
    current_admin_index = get_next_admin_index()
    

    worker_admin, worker_private, nonce = get_address_private_nonce(current_admin_index)


    print(f"DATA: {data} CURRENT ADMIN: {current_admin_index}")
    
    # Check if necessary fields are in the received data
    if 'function_name' not in data or 'function_params' not in data:
        log_flask_error("funciton name or function params does not exist")
        return jsonify(message="JSON value missing"), 500
    
    if data['function_name'] not in function_list:
        log_flask_error("Function does not exist")
        return jsonify(message="Function does not exist"), 500
        # return jsonify(messages = "Error 1001"), 400
    task = admin_action.delay(data,worker_admin, worker_private, nonce)  # Görevi başlat
    

    return jsonify(message="Task added to queue."), 202

