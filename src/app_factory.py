from src.application.profile_service import ProfileService
from src.infrastructure.persistence.profiles_repository import ProfilesRepository
from src.presentation.profile_controller import ProfileController


class AppFactory:
    @staticmethod
    def create(logger):
        profile_repository = ProfilesRepository(logger)
        profile_service = ProfileService(profile_repository, logger)
        profile_controller = ProfileController(profile_service, logger)
        return profile_controller
