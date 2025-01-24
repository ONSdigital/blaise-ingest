import logging
from unittest import mock

import blaise_restapi
import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from tests.helpers import get_default_config
from utilities.custom_exceptions import BlaiseError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


class TestIngest:
    @mock.patch.object(blaise_restapi.Client, "get_ingest")
    def test_get_ingest_calls_the_rest_api_endpoint_with_the_correct_parameters(
        self, _mock_rest_api_client, blaise_service
    ):
        # arrange
        blaise_server_park = "gusty"
        questionnaire_name = "IPS2306a"
        bucket_file_path = 'IPS2306a.zip'
        expected_bucket_file_path = {
            'bucketFilePath': 'IPS2306a.zip'
        }

        # act
        blaise_service.get_ingest(blaise_server_park, questionnaire_name, bucket_file_path)

        # assert
        _mock_rest_api_client.assert_called_with(blaise_server_park, questionnaire_name, expected_bucket_file_path)

