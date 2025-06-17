import logging
from unittest import mock

from main import process_zip_file


@mock.patch("main.ValidationService")
@mock.patch("main.BlaiseService")
@mock.patch("main.Config")
@mock.patch("main.utils")
def test_process_zip_file_questionnaire_does_not_exist(
    mock_utils, mock_config, mock_blaise_service, mock_validation_service, caplog
):
    # Arrange
    data = {"bucket": "test-bucket", "name": "incoming/IPS1234A.zip"}
    context = {}

    mock_config_instance = mock.Mock()
    mock_config.from_env.return_value = mock_config_instance
    mock_config_instance.blaise_server_park = "test-server-park"

    mock_utils.get_questionnaire_name.return_value = "IPS1234A"

    mock_validation_instance = mock_validation_service.return_value
    mock_validation_instance.validate_config.return_value = None
    mock_validation_instance.validate_questionnaire_exists.return_value = False

    caplog.set_level(logging.ERROR)

    # Act
    result = process_zip_file(data, context)

    # Assert
    mock_validation_instance.validate_questionnaire_exists.assert_called_once_with(
        "IPS1234A", mock_config_instance
    )

    assert result == ("IPS1234A does not exist in test-server-park server park", 404)
    assert any(
        "does not exist in test-server-park server park" in message
        for message in caplog.messages
    )


@mock.patch("main.ValidationService")
@mock.patch("main.BlaiseService")
@mock.patch("main.Config")
@mock.patch("main.utils")
def test_process_zip_file_success(
    mock_utils,
    mock_config,
    mock_blaise_service,
    mock_validation_service,
    caplog,
):
    # Arrange
    data = {"bucket": "test-bucket", "name": "incoming/IPS1234A.zip"}
    context = {}

    mock_config_instance = mock.Mock()
    mock_config.from_env.return_value = mock_config_instance
    mock_config_instance.blaise_server_park = "test-server-park"

    mock_utils.get_questionnaire_name.return_value = "IPS1234A"

    mock_validation_instance = mock_validation_service.return_value
    mock_validation_instance.validate_config.return_value = None
    mock_validation_instance.validate_questionnaire_exists.return_value = True

    mock_blaise_instance = mock_blaise_service.return_value
    mock_blaise_instance.get_ingest.return_value = None

    caplog.set_level(logging.INFO)

    # Act
    process_zip_file(data, context)

    # Assert
    mock_validation_instance.validate_questionnaire_exists.assert_called_once_with(
        "IPS1234A", mock_config_instance
    )
    mock_blaise_instance.get_ingest.assert_called_once_with(
        "test-server-park", "IPS1234A", "incoming/IPS1234A.zip"
    )

    assert any("Processing ZIP file: IPS1234A.zip" in m for m in caplog.messages)
    assert any("Finished Running Cloud Function" in m for m in caplog.messages)


@mock.patch("main.ValidationService")
@mock.patch("main.BlaiseService")
@mock.patch("main.Config")
@mock.patch("main.utils")
def test_process_zip_file_skips_non_zip_file(
    mock_utils, mock_config, mock_blaise_service, mock_validation_service, capsys
):
    # Arrange
    data = {"bucket": "test-bucket", "name": "not_a_zip.txt"}
    context = {}

    # Act
    result = process_zip_file(data, context)

    # Assert
    assert result is None
    captured = capsys.readouterr()
    assert "is not a zip file, skipping" in captured.out

    mock_validation_service.return_value.validate_questionnaire_exists.assert_not_called()
    mock_validation_service.return_value.validate_config.assert_not_called()
    mock_config.from_env.assert_not_called()
    mock_utils.get_questionnaire_name.assert_not_called()
    mock_blaise_service.assert_not_called()
