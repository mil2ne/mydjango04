"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()

ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    with ENV_PATH.open(encoding="utf-8") as f:
        env.read_env(f, overwrite=True)
else:
    print("not found:", ENV_PATH)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$#r^!md#5(i17_aw(_e)qo2yqu@kww+lv$far3#7j3@e#5jua^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "accounts",
    "core",
    "core.crispy_bootstrap5_ext",
    "django_extensions",
    "widget_tweaks",
    "hottrack",
    "formtools",
    "blog",
    "school",
    "weblog",
    "shop",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.messages_list",
            ],
        },
    },
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# import pymysql
#
# pymysql.install_as_MySQLdb()
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "HOST": "localhost",  # 서버 주소
#         "PORT": "3306",  # 서버 포트
#         "NAME": "mysql_db",  # 데이터베이스 명
#         "USER": "mysql_user",  # 유저명
#         "PASSWORD": "mysql_pw",  # 암호
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "localhost",  # 서버 주소
        "PORT": "5432",  # 서버 포트
        "NAME": "mydb",  # 데이터베이스 명
        "USER": "myuser",  # 유저명
        "PASSWORD": "mypw",  # 암호
    }
}

AUTH_USER_MODEL = "accounts.User"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        # "OPTIONS": {"max_similarity": 0.5};
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Media
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from django.contrib.messages import constants as messages_constants  # noqa

if DEBUG:
    MESSAGE_LEVEL = messages_constants.DEBUG

if DEBUG:
    FORM_RENDERER = "core.forms.renderers.NoCacheDjangoTemplates"

if DEBUG:
    INSTALLED_APPS += ["django.forms"]

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

if DEBUG:
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE


INTERNAL_IPS = ["127.0.0.1"]
ADMIN_PREFIX = "secret-admin/"


NAVER_MAP_POINT_WIDGET_CLIENT_ID = env.str("NAVER_MAP_POINT_WIDGET_CLIENT_ID")

# LOGIN_REDIRECT_URL = "/accounts/profile/"
LOGIN_REDIRECT_URL = reverse_lazy("accounts:profile")
LOGIN_URL = reverse_lazy("accounts:login")

# if DEBUG:
#     # 이메일을 발송하지 않고, 콘솔에만 표시
#     EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
#
# else:
#     # SMTP를 통해 이메일을 발송
#     EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
#
#     # NAVER SMTP의 경우 : 개인 이메일 서비스이므로 발송량의 제한
#     EMAIL_HOST = "smtp.naver.com"
#     EMAIL_PORT = 465
#     EMAIL_USE_SSL = True
#     EMAIL_HOST_USER = "Naver ID"  # @naver.com을 붙여도 되고 빼도 됩니다.
#     # https://nid.naver.com/user2/help/myInfoV2?m=viewSecurity&lang=ko_KR -> 2단계 인증 관리
#     EMAIL_HOST_PASSWORD = "8----------K"  # 네이버 암호, 2단계 인증이 설정된 경우 별도 설정된 애플리케이션 비밀번호.
#
#     # Google Gmail SMTP의 경우 : 개인 이메일 서비스이므로 발송량의 제한
#     EMAIL_HOST = "smtp.gmail.com"
#     EMAIL_PORT = 587
#     EMAIL_USE_TLS = True
#     EMAIL_HOST_USER = "Gmail ID"  # @gmail.com을 붙여도 되고 빼도 됩니다.
#
#     # 앱 비밀번호 사용을 권장 : Google 계정 (https://myaccount.google.com/security) -> 보안 -> 2단계 인증 -> 앱 비밀번호
#     EMAIL_HOST_PASSWORD = "knjk ---- ---- igsx"

EMAIL_HOST = env.str("EMAIL_HOST", default=None)

if DEBUG and EMAIL_HOST is None:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    try:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

        EMAIL_PORT = env.int("EMAIL_PORT")
        EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
        EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
        EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
        EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
        DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
    except ImproperlyConfigured as e:
        print("Error: ", e, file=sys.stderr)
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
