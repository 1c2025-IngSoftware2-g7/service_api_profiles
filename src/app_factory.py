from src.application.profile_service import ProfileService
from src.infrastructure.persistence.profiles_repository import ProfilesRepository
from src.presentation.profile_controller import ProfileController


class AppFactory:
    @staticmethod
    def create():
        profile_repository = ProfilesRepository()
        profile_service = ProfileService(profile_repository)
        profile_controller = ProfileController(profile_service)
        return profile_controller
