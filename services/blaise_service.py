import logging
from typing import Any, Dict

import blaise_restapi

from appconfig.config import Config
from utilities.custom_exceptions import IngestError
from utilities.logging import function_name


class BlaiseService:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.restapi_client = blaise_restapi.Client(
            f"http://{self._config.blaise_api_url}"
        )

    def get_ingest(
        self, server_park: str, questionnaire_name: str, bucket_file_path: str
    ):
        try:
            data_fields: Dict[str, Any] = {
                "bucketFilePath": bucket_file_path,
            }
            result = self.restapi_client.get_ingest(
                server_park, questionnaire_name, data_fields
            )
            logging.info(f"Got ingest from server park {server_park}: {result}")
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error when ingesting zip file: {e}"
            )
            logging.error(error_message)
            raise IngestError(error_message)
