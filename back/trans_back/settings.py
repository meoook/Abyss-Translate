import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'cse-!!!5$39dd5oq%_pgj6%0&uvx16m*@ovze5z(r79l()ya9l'

DEBUG = True

# ALLOWED_HOSTS = ['192.168.1.20', ]
ALLOWED_HOSTS = ['*']


# Application definition
MY_APPS = [
    'rest_framework',
    'knox',
    'core',
    'accounts',
    'corsheaders',                                              # REMOVE IN PROD
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
    'corsheaders.middleware.CorsMiddleware',                    # REMOVE IN PROD
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trans_back.urls'

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

WSGI_APPLICATION = 'trans_back.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'abby',
        'USER': 'postgres',
        'PASSWORD': '111',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
# TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
# If you set this to True, Django will format dates, numbers and calendars
# according to user current locale.
USE_L10N = False
USE_TZ = True
# Default charset to use for all HttpResponse objects, if a MIME type isn't
# manually specified. It's used to construct the Content-Type header.
DEFAULT_CHARSET = 'utf-8'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# MEDIA_URL = '/media/'   # Opened in urls
MEDIA_ROOT = os.path.join(BASE_DIR, 'users')

STATIC_URL = '/source/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [
#     ("js", os.path.join(STATIC_ROOT, 'js')),
#     ("css", os.path.join(STATIC_ROOT, 'css')),
#     ("img", os.path.join(STATIC_ROOT, 'img')),
# ]
# Maximum size, in bytes, of a request before it will be streamed to the
# file system instead of into memory.
# FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB

# Maximum size in bytes of request data (excluding file uploads) that will be
# read before a SuspiciousOperation (RequestDataTooBig) is raised.
# DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB
# The numeric mode to set newly-uploaded files to. The value should be a mode
# you'd pass directly to os.chmod; see https://docs.python.org/library/os.html#files-and-directories.
# FILE_UPLOAD_PERMISSIONS = 0o644
# Default short formatting for date objects. See all available format strings here:
# https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
# SHORT_DATE_FORMAT = 'm/d/Y'

from django.core.files.storage import FileSystemStorage
STORAGE_ROOT = FileSystemStorage(location=MEDIA_ROOT, base_url='/users/')
STORAGE_ERRORS = FileSystemStorage(location=os.path.join(MEDIA_ROOT, 'errors'), base_url='/errors/')
STORAGE_EXPORT = FileSystemStorage(location=os.path.join(MEDIA_ROOT, 'export'), base_url='/download/')

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser', ]
}


# If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect         # REMOVE IN PROD
# CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://192.168.1.20:3000',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://192.168.1.20:3000',
]
