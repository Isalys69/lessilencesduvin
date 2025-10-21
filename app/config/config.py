from datetime import timedelta
import os

class Config:
    ...
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_LIFETIME_HOURS", 2))
    )
