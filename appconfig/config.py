import os
from dataclasses import dataclass


@dataclass
class Config:
    blaise_api_url: str
    blaise_server_park: str

    @classmethod
    def from_env(cls):
        return cls(
            blaise_api_url=os.getenv("BLAISE_API_URL"),
            blaise_server_park=os.getenv("BLAISE_SERVER_PARK"),
        )

    def log(self):
        print(f"Configuration: Blaise API Url: {self.blaise_api_url}")
        print(f"Configuration: Blaise Server Park: {self.blaise_server_park}")
