from flask import jsonify, current_app
from src.headers import (
    PROFILE_CREATED,
    BAD_REQUEST,
    PROFILE_NOT_FOUND,
    SERVER_ERROR,
)
from src.application.profile_service import ProfileService
from src.presentation.error_generator import get_error_json


class ProfileController:
    def __init__(self, profile_service: ProfileService):
        self.profile_service = profile_service

    def create_profile(self, request):
        if not request.is_json:
            return {"response": jsonify({"error": BAD_REQUEST}), "code_status": 400}

        try:
            profile_data = request.get_json()

            valid_roles = ["student", "teacher", "admin"]
            if "role" in profile_data and profile_data["role"] not in valid_roles:
                return {
                    "response": jsonify(
                        {
                            "error": "Invalid role",
                            "detail": f"Role must be one of: {', '.join(valid_roles)}",
                        }
                    ),
                    "code_status": 400,
                }

            # Crear el perfil
            self.profile_service.create_profile(profile_data)

            return {
                "response": jsonify({"message": PROFILE_CREATED, "data": profile_data}),
                "code_status": 201,
            }

        except ValueError as e:
            return {
                "response": jsonify({"error": BAD_REQUEST, "detail": str(e)}),
                "code_status": 400,
            }
        except Exception as e:
            current_app.logger.error(f"Profile API - Error creating profile: {str(e)}")
            return {
                "response": jsonify(
                    {"error": SERVER_ERROR, "detail": "Internal server error"}
                ),
                "code_status": 500,
            }

    def get_specific_profiles(self, uuid, public_view=False):
        try:
            profile = self.profile_service.get_specific_profile(uuid)

            if not profile:
                return {
                    "response": jsonify(
                        {
                            "type": "about:blank",
                            "title": PROFILE_NOT_FOUND,
                            "status": 404,
                            "detail": f"Profile with UUID {uuid} not found",
                            "instance": f"/profiles/{uuid}",
                        }
                    ),
                    "code_status": 404,
                }

            if public_view:
                # Solo campos públicos
                response_data = {
                    "display_name": profile.display_name,
                    "phone": profile.phone,
                    "birthday": profile.birthday,
                    "gender": profile.gender,
                    "description": profile.description,
                    "display_image": profile.display_image,
                }
            else:
                # Todos los campos (vista privada)
                response_data = {
                    "uuid": profile.uuid,
                    "email": profile.email,
                    "role": profile.role,
                    "display_name": profile.display_name,
                    "location": profile.location,
                    "birthday": profile.birthday,
                    "gender": profile.gender,
                    "description": profile.description,
                    "display_image": profile.display_image,
                    "phone": profile.phone,
                }

            return {"response": jsonify({"data": response_data}), "code_status": 200}

        except Exception as e:
            current_app.logger.error(f"Profile API - Error fetching profile: {str(e)}")
            return {
                "response": jsonify(
                    {"error": SERVER_ERROR, "detail": "Internal server error"}
                ),
                "code_status": 500,
            }

    def modify_profile(self, request):
        if not request.is_json:
            return {"response": jsonify({"error": BAD_REQUEST}), "code_status": 400}

        try:
            data = request.get_json()
            uuid = data.get("uuid")
            updates = data.get("updates")

            # Validaciones básicas
            if not uuid or not updates:
                return {
                    "response": jsonify({"error": "UUID and updates are required"}),
                    "code_status": 400,
                }

            # Campos no modificables
            if "email" in updates or "password" in updates:
                return {
                    "response": jsonify(
                        {"error": "Email and password cannot be modified"}
                    ),
                    "code_status": 400,
                }

            # Validar campos permitidos
            allowed_fields = [
                "display_name",
                "location",
                "birthday",
                "gender",
                "description",
                "display_image",
                "phone",
            ]
            for field in updates.keys():
                if field not in allowed_fields:
                    return {
                        "response": jsonify(
                            {"error": f"Field '{field}' cannot be modified"}
                        ),
                        "code_status": 400,
                    }

            # Validar rol si está presente
            if "role" in updates:
                valid_roles = ["student", "teacher", "admin"]
                if updates["role"] not in valid_roles:
                    return {
                        "response": jsonify(
                            {
                                "error": "Invalid role",
                                "detail": f"Role must be one of: {', '.join(valid_roles)}",
                            }
                        ),
                        "code_status": 400,
                    }

            # Actualizar el perfil
            updated_profile = self.profile_service.modify_profile(uuid, updates)

            return {
                "response": jsonify(
                    {
                        "message": "Profile updated successfully",
                        "data": {
                            "uuid": updated_profile.uuid,
                            "updated_fields": updates,
                        },
                    }
                ),
                "code_status": 200,
            }

        except ValueError as e:
            return {
                "response": jsonify({"error": BAD_REQUEST, "detail": str(e)}),
                "code_status": 400,
            }
        except Exception as e:
            current_app.logger.error(f"Profile API - Error modifying profile: {str(e)}")
            return {"response": jsonify({"error": SERVER_ERROR}), "code_status": 500}

    def upload_image(self, request):
        if not request.is_json:
            return {"response": jsonify({"error": BAD_REQUEST}), "code_status": 400}
        data = request.get_json()

        if 'image' not in data or 'uuid' not in data:
            return {
                "response": get_error_json("Image and UUID are required", "Missing image or UUID in the request", "/upload", "POST"),
                "code_status": 400,
            }
        uuid = data.get("uuid")
        image = data.get("image")

        if image.filename == '':
            return {
                "response": get_error_json("No selected file", "Missing image.filename in the request", "/upload", "POST"),
                "code_status": 400,
            }

        url = self.profile_service.add_image(uuid, image)

        return {
            "response": jsonify({
                "message": "Image uploaded",
                "uuid": uuid,
                "url": url
            }),
            "code_status": 200,
        }
