import logging

import blaise_restapi

from appconfig.config import Config
from utilities.custom_exceptions import BlaiseError, ConfigError
from utilities.logging import function_name


class ValidationService:
    def __init__(self) -> None:
        self.request_json = None

    @staticmethod
    def validate_config(config):
        missing_configs = []
        if config.blaise_api_url is None or config.blaise_api_url == "":
            missing_configs.append("blaise_api_url")
        if config.blaise_server_park is None or config.blaise_server_park == "":
            missing_configs.append("blaise_server_park")

        if missing_configs:
            error_message = f"Missing required values from config: {missing_configs}"
            logging.error(error_message)
            raise ConfigError(error_message)

    @staticmethod
    def validate_questionnaire_exists(questionnaire_name: str, config: Config):
        server_park = config.blaise_server_park
        restapi_client = blaise_restapi.Client(f"http://{config.blaise_api_url}")

        try:
            restapi_client.questionnaire_exists_on_server_park(
                server_park, questionnaire_name
            )
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error checking questionnaire '{questionnaire_name}' exists: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)
