from contextlib import contextmanager
from unittest import mock

import blaise_restapi
import pytest

import services
import utils
from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.validation_service import ValidationService
from tests.helpers import get_default_config
from utilities.custom_exceptions import BlaiseError, ConfigError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


class TestUtils:

    @pytest.mark.parametrize(
        "file_name, questionnaire_name",
        [
            ("IPS2501A.zip", "IPS2501A"),
            ("IPS2501A_AA1.zip", "IPS2501A_AA1"),
            ("IPS2502.zip", "IPS2502"),
            ("IPS2503_edit.zip", "IPS2503_edit"),
            ("IPS2503_edit", None),
            ("IPS2501A_AA1.Zip", "IPS2501A_AA1"),
        ],
    )
    def test_get_questionnaire_name(self, file_name, questionnaire_name):
        # arrange
        result = utils.get_questionnaire_name(file_name)

        # assert
        assert result == questionnaire_name


class TestValidateConfig:

    @pytest.mark.parametrize(
        "blaise_api_url, blaise_server_park",
        [
            (None, None),
            ("", None),
            (None, ""),
            ("", ""),
        ],
    )
    def test_validate_config_logs_and_raises_validation_error_exception_when_both_config_values_are_missing(
        self, blaise_api_url, blaise_server_park, caplog
    ):
        # arrange
        mock_config = Config(
            blaise_api_url=blaise_api_url, blaise_server_park=blaise_server_park
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(ConfigError) as err:
            validation_service.validate_config(mock_config)

        # assert
        error_message = "Missing required values from config: ['blaise_api_url', 'blaise_server_park']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_api_url",
        [None, ""],
    )
    def test_validate_config_logs_and_raises_validation_error_exception_when_blaise_api_url_is_missing(
        self, blaise_api_url, caplog
    ):
        # arrange
        mock_config = Config(blaise_api_url=blaise_api_url, blaise_server_park="bar")
        validation_service = ValidationService()

        # act
        with pytest.raises(ConfigError) as err:
            validation_service.validate_config(mock_config)

        # assert
        error_message = "Missing required values from config: ['blaise_api_url']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_server_park",
        [None, ""],
    )
    def test_validate_config_logs_and_raises_validation_error_exception_when_blaise_server_park_is_missing(
        self, blaise_server_park, caplog
    ):
        # arrange
        mock_config = Config(
            blaise_api_url="foo", blaise_server_park=blaise_server_park
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(ConfigError) as err:
            validation_service.validate_config(mock_config)

        # assert
        error_message = "Missing required values from config: ['blaise_server_park']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples


class TestIngest:
    @mock.patch.object(blaise_restapi.Client, "get_ingest")
    def test_get_ingest_calls_the_rest_api_endpoint_with_the_correct_parameters(
        self, _mock_rest_api_client, blaise_service
    ):
        # arrange
        blaise_server_park = "gusty"
        questionnaire_name = "IPS2306a"
        bucket_file_path = "IPS2306a.zip"
        expected_bucket_file_path = {"bucketFilePath": "IPS2306a.zip"}

        # act
        blaise_service.get_ingest(
            blaise_server_park, questionnaire_name, bucket_file_path
        )

        # assert
        _mock_rest_api_client.assert_called_with(
            blaise_server_park, questionnaire_name, expected_bucket_file_path
        )


class TestValidateQuestionnaireExists:
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_validate_questionnaire_exists_does_not_raise_an_exception_when_questionnaire_exists(
        self, mock_questionnaire_exists_on_server_park
    ):
        # arrange
        mock_questionnaire_exists_on_server_park.return_value = {
            "questionnaire_name": "IPS2403a"
        }
        validation_service = ValidationService()
        mock_questionnaire_name = "IPS2403a"
        mock_config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # assert
        with does_not_raise(BlaiseError):
            validation_service.validate_questionnaire_exists(
                mock_questionnaire_name, mock_config
            )

    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_validate_questionnaire_exists_logs_and_raises_a_blaise_error_exception_when_rest_api_fails(
        self, mock_questionnaire_exists_on_server_park, caplog
    ):
        # arrange
        mock_questionnaire_exists_on_server_park.side_effect = Exception(
            "Bendybug Cannotkrump"
        )
        validation_service = ValidationService()
        mock_questionnaire_name = "IPS2403a"
        mock_config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # act
        with pytest.raises(BlaiseError) as err:
            validation_service.validate_questionnaire_exists(
                mock_questionnaire_name, mock_config
            )

        # assert
        error_message = (
            "Exception caught in validate_questionnaire_exists(). "
            "Error checking questionnaire 'IPS2403a' exists: Bendybug Cannotkrump"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    def test_validate_config_does_not_raise_an_exception_when_given_valid_config(self):
        # arrange
        validation_service = ValidationService()
        mock_config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # assert
        with does_not_raise(ConfigError):
            validation_service.validate_config(mock_config)


class TestProcessZipFile:

    @mock.patch.object(
        services.validation_service.ValidationService, "validate_questionnaire_exists"
    )
    def test_validation_questionnaire_exists(self, mock_validate_questionnaire_exists):
        # arrange
        validation_service = ValidationService()
        questionnaire_name = "IPS2501A"
        config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # act
        validation_service.validate_questionnaire_exists(questionnaire_name, config)

        # assert
        assert mock_validate_questionnaire_exists.called_with(
            questionnaire_name, config
        )

    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_validate_questionnaire_exists(
        self, mock_questionnaire_exists_on_server_park, caplog
    ):
        # Arrange
        validation_service = ValidationService()
        questionnaire_name = "IPS2501A"
        config = Config(blaise_api_url="foo", blaise_server_park="bar")
        mock_questionnaire_exists_on_server_park.return_value = True

        # Act
        result = validation_service.validate_questionnaire_exists(
            questionnaire_name, config
        )

        # Assert mock was called
        assert mock_questionnaire_exists_on_server_park.called_with(
            questionnaire_name, config
        )
        assert result is True

    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_validate_questionnaire_does_not_exist(
        self, mock_questionnaire_exists_on_server_park, caplog
    ):
        # Arrange
        validation_service = ValidationService()
        questionnaire_name = "silly_name"
        config = Config(blaise_api_url="foo", blaise_server_park="bar")
        mock_questionnaire_exists_on_server_park.return_value = False

        # Act
        result = validation_service.validate_questionnaire_exists(
            questionnaire_name, config
        )

        # Assert mock was called
        assert mock_questionnaire_exists_on_server_park.called_with(
            questionnaire_name, config
        )
        assert result is False


@contextmanager
def does_not_raise(expected_exception):
    try:
        yield

    except expected_exception as error:
        raise AssertionError(f"Raised exception {error} when it should not!")

    except Exception as error:
        raise AssertionError(f"An unexpected exception {error} raised.")
