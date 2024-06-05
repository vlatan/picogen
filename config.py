from dataclasses import dataclass


@dataclass(frozen=True)
class Config:

    SITE_URL: str
    SITE_NAME: str
    SITE_TAGLINE: str

    THEME: str = "default"
    GTAG_ID: str | None = None
    CONTACT_EMAIL: str | None = None
