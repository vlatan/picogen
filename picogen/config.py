from dataclasses import dataclass


@dataclass(frozen=True)
class Config:

    SITE_URL: str = "http:localhost:8000"
    SITE_NAME: str = "Hello World"
    SITE_TAGLINE: str = "Example tagline"

    THEME: str = "default"
    GTAG_ID: str | None = None
    CONTACT_EMAIL: str | None = None
