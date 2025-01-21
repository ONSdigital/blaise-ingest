import logging
import flask

from services.validation_service import ValidationService
from appconfig.config import Config
from services.guid_service import GUIDService
from services.user_service import UserService
from services.blaise_service import BlaiseService
from utilities.logging import setup_logger

setup_logger()


def ingest_data(request: flask.request) -> tuple[str, int]:
    try:
        logging.info("Running Cloud Function - 'ingest data'")
        validation_service = ValidationService()

        # Request Handler
        questionnaire_name, user = (
            validation_service.get_valid_request_values_for_ingest_service(
                request
            )
        )

        # Config Handler
        blaise_config = Config.from_env()
        validation_service.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

        # Blaise Handler
        blaise_service = BlaiseService(blaise_config)
        validation_service.validate_questionnaire_exists(
            questionnaire_name, blaise_config
        )

        # GUID Handler
        guid_service = GUIDService(blaise_service)
        guid = guid_service.get_guid(blaise_server_park, questionnaire_name)

        # User Handler
        user_service = UserService(blaise_service)
        user_service.get_user_by_name(blaise_server_park, user)

        # Ingest Handler
        donor_case_service = IngestService(blaise_service)
        donor_case_service.reissue_new_donor_case_for_user(
            questionnaire_name, guid, user
        )

        logging.info("Finished Running Cloud Function - 'reissue_new_donor_case'")
        return f"Successfully reissued new donor case for user: {user}", 200
    except (RequestError, AttributeError, ValueError, ConfigError) as e:
        error_message = f"Error reissuing IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 400
    except BlaiseError as e:
        error_message = f"Error reissuing IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 404
    except (GuidError, UsersError, DonorCaseError, Exception) as e:
        error_message = f"Error reissuing IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 500