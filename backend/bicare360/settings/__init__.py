"""
Settings package for bicare360.
Loads appropriate settings based on ENVIRONMENT variable.
"""
import os

environment = os.environ.get("ENVIRONMENT", "development")

if environment == "production":
    from .prod import *
elif environment == "test":
    from .test import *
else:
    from .dev import *
