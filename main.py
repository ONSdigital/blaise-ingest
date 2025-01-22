import logging
import flask

from services.ingest_service import IngestService
from services.validation_service import ValidationService
from appconfig.config import Config
from services.guid_service import GUIDService
from services.user_service import UserService
from services.blaise_service import BlaiseService
from utilities.logging import setup_logger
from utilities.custom_exceptions import (
    BlaiseError,
    ConfigError,
    GuidError,
    QuestionnaireNotFound,
    RequestError,
    UsersError,
    UsersWithRoleNotFound, IngestError,
)
from google.cloud import storage

setup_logger()


def process_zip_file(data, context):
    try:
        logging.info("Running Cloud Function - 'ingest data'")
        validation_service = ValidationService()

        file = data
        bucket_name = file['bucket']
        file_name = file['name']

        # Only trigger on .zip files
        if not file_name.endswith('.zip'):
            print(f"File {file_name} is not a zip file, skipping.")
            return

        print(f"Processing ZIP file: {file_name}")

        # Initialize the client
        storage_client = storage.Client()

        # Reference to the bucket
        bucket = storage_client.get_bucket(bucket_name)

        # Get the uploaded ZIP file
        blob = bucket.blob(file_name)

        # Debug: Print out the file's metadata
        print(f"File {file_name} uploaded to {bucket_name}.")
        print(f"Blob size: {blob.size} bytes")

        # Config Handler
        blaise_config = Config.from_env()
        validation_service.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

        # Blaise Handler TODO: Get questionnaire_name from somewhere and validate it exists
        # validation_service.validate_questionnaire_exists(
        #     questionnaire_name, blaise_config
        # )
        questionnaire_name = file['questionnaire']

        # Ingest Handler
        blaise_service = BlaiseService(blaise_config)
        ingest_service = IngestService(blaise_service)
        ingest_service.ingest(blaise_server_park, questionnaire_name)

        logging.info("Finished Running Cloud Function - 'ingest data'")
        return f"Successfully ingested file from bucket", 200
    except (RequestError, AttributeError, ValueError, ConfigError) as e:
        error_message = f"Error occurred during Ingest: {e}"
        logging.error(error_message)
        return error_message, 400
    except BlaiseError as e:
        error_message = f"Error occurred during Ingest: {e}"
        logging.error(error_message)
        return error_message, 404
    except (GuidError, UsersError, IngestError, Exception) as e:
        error_message = f"Error occurred during Ingest: {e}"
        logging.error(error_message)
        return error_message, 500
