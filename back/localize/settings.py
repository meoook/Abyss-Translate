import os
from django.core.files.storage import FileSystemStorage

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY", "NO_KEY_WARNING")
DEBUG = os.environ.get("DEBUG", True)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(" ")

# Application definition
MY_APPS = [
    'corsheaders',
    'rest_framework',
    'knox',
    'core',
    'accounts',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + MY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'localize.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'localize.wsgi.application'
# Database
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("SQL_DATABASE", "postgres"),
        "USER": os.environ.get("SQL_USER", "postgres"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "xaxaxue"),
        "HOST": os.environ.get("SQL_HOST", "postgres"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
        "TEST": {'NAME': 'test_postgres'},
    }
}


AUTH_USER_MODEL = 'accounts.UserProfile'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")

USE_I18N = True
USE_L10N = False
USE_TZ = True
DEFAULT_CHARSET = 'utf-8'

# Files Storage
MEDIA_ROOT = os.path.join(BASE_DIR, 'users')
STATIC_URL = '/source/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Maximum size, in bytes, of a request before it will be streamed to the
# file system instead of into memory.
# FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB

# Maximum size in bytes of request data (excluding file uploads) that will be
# read before a SuspiciousOperation (RequestDataTooBig) is raised.
# DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024
# The numeric mode to set newly-uploaded files to. The value should be a mode
# you'd pass directly to os.chmod; see https://docs.python.org/library/os.html#files-and-directories.
# FILE_UPLOAD_PERMISSIONS = 0o644
# Default short formatting for date objects. See all available format strings here:
# https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
# SHORT_DATE_FORMAT = 'm/d/Y'

STORAGE_ROOT = FileSystemStorage(location=MEDIA_ROOT, base_url='/users/')
STORAGE_ERRORS = FileSystemStorage(location=os.path.join(MEDIA_ROOT, 'errors'), base_url='/errors/')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser', ],
}

# If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
# CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
CORS_ORIGIN_WHITELIST = [
    'http://localhost',
    'http://localhost:3000',
    'http://127.0.0.1',
    'http://127.0.0.1:3000',
    'http://91.225.238.193:3000',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://localhost',
    r"^http://.+\:3000.*$"
    'http://127.0.0.1:3000',
    'http://91.225.238.193:3000',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CSRF_TRUSTED_ORIGINS = [
    '127.0.0.1',
    'localhost'
]

# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")
CELERYBEAT_SCHEDULE_FILENAME = os.environ.get("CELERYBEAT_SCHEDULE_FILENAME", "celerybeat-schedule")

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = True

# CELERY_DEFAULT_RATE_LIMIT = '20/m'
# CELERYD_SOFT_TIME_LIMIT = 45
# CELERYD_TIME_LIMIT = 60

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sql': {
            'format': '[SQL {module} {duration:f}] {sql}',
            'style': '{',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'file': {
            'format': '[{asctime} {levelname}/{module}] {message}',
            'style': '{',
            'datefmt': '%d/%m/%Y %H:%M:%S',
        },
        'full': {
            'format': '[{asctime} {levelname}/{name} in {module}] {message}',
            'style': '{',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname:.4} {module}] {message}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'sql': {
            'level': 'WARNING',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
        },
        'debug': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'full',
        },
        'file': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'log.log'),
            'formatter': 'file',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'email_backend': 'django.core.mail.backends.filebased.EmailBackend',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file', 'debug'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'file', 'debug'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['sql'],
            'level': 'DEBUG',   # set DEBUG for debug sql queries :)
            'propagate': False,
        },
        'logfile': {
            'handlers': ['file'],
            'level': 'INFO',    # When to log in file
            'propagate': True,
        },
        'django.mail': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',   # When to send mails
            'propagate': True,
        },
    },
}

