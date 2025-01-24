import os
from unittest import mock

from appconfig.config import Config


def test_config():
    config = Config(
        blaise_api_url="foobar",
        blaise_server_park="foobar",
    )
    assert config.blaise_api_url == "foobar"
    assert config.blaise_server_park == "foobar"


@mock.patch.dict(
    os.environ,
    {
        "BLAISE_API_URL": "test_blaise_api_url",
        "BLAISE_SERVER_PARK": "test_blaise_server_park",
    },
)
def test_config_from_env():
    config = Config.from_env()
    assert config.blaise_api_url == "test_blaise_api_url"
    assert config.blaise_server_park == "test_blaise_server_park"
