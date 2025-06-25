from datetime import timedelta
import os
from flask import Flask, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from src.app_factory import AppFactory
from src.logger_config import get_logger

profiles_app = Flask(__name__)
CORS(profiles_app)

# Session config
profiles_app.secret_key = os.getenv("SECRET_KEY_SESSION")
profiles_app.permanent_session_lifetime = timedelta(minutes=5)

# Logger config
logger = get_logger("api-profiles")

profile_controller = AppFactory.create()

SWAGGER_URL = "/docs"
API_URL = "/static/openapi.yaml"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Profiles API"}
)
profiles_app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@profiles_app.get("/health")
def health_check():
    return {"status": "ok"}, 200


@profiles_app.post("/profiles")
def create_profile():
    """
    Create a new profile.
    Expects JSON with: uuid, name, surname, email, etc.
    """
    result = profile_controller.create_profile(request)
    return result["response"], result["code_status"]


# curl - X POST http: // localhost: 8081/profiles - H "Content-Type: application/json" - d '{"uuid": "123e4567-e89b-12d3-a456-426614174000","email": "usuario@ejemplo.com","role": "student"}'


@profiles_app.get("/profiles")
def get_all_profile():
    result = profile_controller.get_all_profiles()
    return result["response"], result["code_status"]


@profiles_app.get("/profiles/<uuid:uuid>")
def get_private_profile(uuid):
    result = profile_controller.get_specific_profiles(uuid, public_view=False)
    return result["response"], result["code_status"]


# curl - X GET http: // localhost: 8081/profiles/123e4567-e89b-12d3-a456-426614174000


@profiles_app.get("/profiles/public/<uuid:uuid>")
def get_public_profile(uuid):
    result = profile_controller.get_specific_profiles(uuid, public_view=True)
    return result["response"], result["code_status"]


# curl - X GET http: // localhost: 8081/profiles/public/123e4567-e89b-12d3-a456-426614174000


@profiles_app.put("/profiles/modify")
def modify_profile():
    result = profile_controller.modify_profile(request)
    return result["response"], result["code_status"]


# curl - X PUT http: // localhost: 8081/profiles/modify - H "Content-Type: application/json" - d '{ "uuid": "123e4567-e89b-12d3-a456-426614174000", "updates": { "display_name": "Nuevo nombre", "location": "New York"}}'


@profiles_app.post("/upload")
def upload_image():
    result = profile_controller.upload_image(request)
    return result["response"], result["code_status"]
