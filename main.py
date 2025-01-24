import logging

from google.cloud import storage

import utils
from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.validation_service import ValidationService
from utilities.custom_exceptions import (
    BlaiseError,
    ConfigError,
    GuidError,
    IngestError,
    RequestError,
    UsersError,
)
from utilities.logging import setup_logger

setup_logger()


def process_zip_file(data):
    try:
        logging.info("Running Cloud Function - 'ingest data'")
        validation_service = ValidationService()

        file = data
        bucket_name = file["bucket"]
        file_name = file["name"]

        # Only trigger on .zip files
        if not file_name.endswith(".zip"):
            print(f"File {file_name} is not a zip file, skipping.")
            return

        print(f"Processing ZIP file: {file_name} from bucket {bucket_name}")

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

        questionnaire_name = utils.get_questionnaire_name(file_name)

        # Blaise Handler
        validation_service.validate_questionnaire_exists(
            questionnaire_name, blaise_config
        )

        # Ingest Handler
        blaise_service = BlaiseService(blaise_config)

        logging.info(
            f"Calling Ingest Service with "
            f"server park: {blaise_server_park}, "
            f"questionnaire name: {questionnaire_name}, "
            f"file name: {file_name}"
        )
        blaise_service.get_ingest(blaise_server_park, questionnaire_name, file_name)
        logging.info("Finished Running Cloud Function - 'ingest data'")

        return f"Successfully ingested {file_name} from bucket", 200

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


# Testing
process_zip_file()
