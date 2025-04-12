from datetime import timedelta
import logging
import os
from flask import Flask, request
from flask_cors import CORS
from src.app_factory import AppFactory

profiles_app = Flask(__name__)
CORS(profiles_app)

# Session config
profiles_app.secret_key = os.getenv("SECRET_KEY_SESSION")
profiles_app.permanent_session_lifetime = timedelta(minutes=5)

env = os.getenv("FLASK_ENV")
log_level = logging.DEBUG if env == "development" else logging.INFO
profiles_app.logger.setLevel(log_level)
profiles_logger = profiles_app.logger
profile_controller = AppFactory.create(profiles_logger)

@profiles_app.get("/health")
def health_check():
    return {"status": "ok"}, 200


"""
Create a new profile.
Expects JSON with: uuid, name, surname, email, etc.
"""
@profiles_app.post("/profiles")
def create_profile():
    result = profile_controller.create_profile(request)
    return result["response"], result["code_status"]


@profiles_app.get("/profiles/<uuid:uuid>")
def get_specific_profiles(uuid):
    result = profile_controller.get_specific_profiles(uuid)
    return result["response"], result["code_status"]


@profiles_app.put("/profiles/modify")
def modify_profile():
    result = profile_controller.modify_profile(request)
    return result["response"], result["code_status"]
