from flask import jsonify
from src.headers import PROFILE_CREATED, BAD_REQUEST, PROFILE_ALREADY_EXISTS, SERVER_ERROR
from src.application.profile_service import ProfileService


class ProfileController:
    def __init__(self, profile_service: ProfileService, logger):
        self.profile_service = profile_service
        self.log = logger

    def create_profile(self, request):
        if not request.is_json:
            return {
                "response": jsonify({"error": BAD_REQUEST}),
                "code_status": 400
            }

        try:
            profile_data = request.get_json()

            valid_roles = ['student', 'teacher', 'admin']
            if 'role' in profile_data and profile_data['role'] not in valid_roles:
                return {
                    "response": jsonify({
                        "error": "Invalid role",
                        "detail": f"Role must be one of: {', '.join(valid_roles)}"
                    }),
                    "code_status": 400
                }

            # Crear el perfil
            self.profile_service.create_profile(profile_data)

            return {
                "response": jsonify({
                    "message": PROFILE_CREATED,
                    "data": profile_data
                }),
                "code_status": 201
            }

        except ValueError as e:
            return {
                "response": jsonify({
                    "error": BAD_REQUEST,
                    "detail": str(e)
                }),
                "code_status": 400
            }
        except Exception as e:
            self.log.error(f"Error creating profile: {str(e)}")
            return {
                "response": jsonify({
                    "error": SERVER_ERROR,
                    "detail": "Internal server error"
                }),
                "code_status": 500
            }
