import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, IngestError
from utilities.logging import function_name


class IngestService:
    def __init__(self, blaise_service: BlaiseService) -> None:
        self._blaise_service = blaise_service

    @staticmethod
    def assert_expected_number_of_things(  # TODO: what is in the zip?
        expected_number_of_things: int, total_things: int
    ):
        if expected_number_of_things != total_things:
            logging.info(
                f"Expected to create {expected_number_of_things} things. Only created {total_things}"
            )
        else:
            logging.info(
                f"Expected to create {expected_number_of_things} things. Successfully Created {total_things} things"
            )

    def ingest(  # TODO: what is in the zip?
        self, server_park_name: str, questionnaire_name: str
    ) -> None:
        try:
            self._blaise_service.get_ingest(server_park_name, questionnaire_name)
        except BlaiseError as e:
            raise BlaiseError(e.message)
        except IngestError as e:
            raise IngestError(e.message)
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error when checking and creating zip thing: {e}"
            )
            logging.error(error_message)
            raise IngestError(error_message)

        