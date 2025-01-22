import logging
from typing import Any, Dict

import blaise_restapi

from appconfig.config import Config
from utilities.custom_exceptions import BlaiseError
from utilities.logging import function_name
from utilities.regex import extract_username_from_case_id


class BlaiseService:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.restapi_client = blaise_restapi.Client(
            f"http://{self._config.blaise_api_url}"
        )

        self.cma_serverpark_name = "cma"
        self.cma_questionnaire = "CMA_Launcher"

    def get_questionnaire(
        self, server_park: str, questionnaire_name: str
    ) -> Dict[str, Any]:
        try:
            questionnaire = self.restapi_client.get_questionnaire_for_server_park(
                server_park, questionnaire_name
            )
            logging.info(f"Got questionnaire '{questionnaire_name}'")
            return questionnaire
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting questionnaire '{questionnaire_name}': {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def get_users(self, server_park: str) -> dict[str, Any]:
        try:
            return self.restapi_client.get_users()
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting users from server park {server_park}: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def get_questionnaire_cases(self, guid: str) -> dict[str, Any]:
        try:
            cases = self.restapi_client.get_questionnaire_data(
                self.cma_serverpark_name,
                self.cma_questionnaire,
                ["MainSurveyID", "id", "CMA_IsDonorCase"],
                f"MainSurveyID='{guid}'",
            )
            return cases
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting questionnaire cases from server park {self.cma_serverpark_name}: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def get_ingest(self, server_park: str, questionnaire_name: str): # TODO: stuff
        try:
            result = self.restapi_client.get_ingest(server_park, questionnaire_name)
            logging.info(f"Got ingest from server park {server_park}: {result}")
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting existing get ingest: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)