import logging
import re

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, DonorCaseError
from utilities.logging import function_name
from utilities.regex import extract_username_from_case_id


class IngestService:
    def __init__(self, blaise_service: BlaiseService) -> None:
        self._blaise_service = blaise_service

    @staticmethod
    def assert_expected_number_of_things( # TODO: what is in the zip?
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


    def check_and_create_zip_thing( # TODO: what is in the zip?
        self, questionnaire_name: str, guid: str, users_with_role: list
    ) -> None:
        total_things_created = 0
        try:
            users_with_existing_donor_cases = (
                self._blaise_service.get_all_existing_donor_cases(guid)
            )
            for user in users_with_role:
                if self.donor_case_does_not_exist(
                    user, users_with_existing_donor_cases
                ):
                    donor_case_model = DonorCaseModel(user, questionnaire_name, guid)
                    self._blaise_service.create_donor_case_for_user(donor_case_model)
                    total_donor_cases_created += 1
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

        