# This file includes overrides to build the `development` environment for the LMS starting from the
# settings of the `production` environment

from docker_run_production import *
from .utils import Configuration

# Load custom configuration parameters from yaml files
config = Configuration(os.path.dirname(__file__))

DEBUG = True
REQUIRE_DEBUG = True

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

PIPELINE_ENABLED = False
STATICFILES_STORAGE = "openedx.core.storage.DevelopmentStorage"

ALLOWED_HOSTS = ["*"]

WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

LTI_XBLOCK_CONFIGURATIONS = config(
    "LTI_XBLOCK_CONFIGURATIONS", default=[], formatter=json.loads
)
LTI_XBLOCK_SECRETS = config(
    "LTI_XBLOCK_SECRETS", default={}, formatter=json.loads
)
