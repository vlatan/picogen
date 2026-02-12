import os
from dataclasses import dataclass


@dataclass
class Config:

    SITE_URL: str = "http:localhost:8000"
    SITE_NAME: str = "Hello World"
    SITE_TAGLINE: str = "Example tagline"

    THEME: str = "default"
    GTAG_ID: str = ""
    CONTACT_EMAIL: str = ""

    def __post_init__(self):
        self.SITE_URL = os.getenv("SITE_URL", self.SITE_URL)
        self.SITE_NAME = os.getenv("SITE_NAME", self.SITE_NAME)
        self.SITE_TAGLINE = os.getenv("SITE_TAGLINE", self.SITE_TAGLINE)

        self.THEME = os.getenv("THEME", self.THEME)
        self.GTAG_ID = os.getenv("GTAG_ID", self.GTAG_ID)
        self.CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", self.CONTACT_EMAIL)
