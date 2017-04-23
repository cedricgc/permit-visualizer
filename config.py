# -*- coding: utf-8 -*-


import os


class Config():
    # Determine code location in file system
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FILES = os.path.join(BASE_DIR, 'static')
    TEMPLATES = os.path.join(BASE_DIR, 'templates')

    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URI')

    # 3rd Party configuration
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

    # Flask configuration: see http://flask.pocoo.org/docs/latest/config/

    # By default Flask serializes objects to ascii-encoded JSON.
    # If this is set to False Flask will not encode to ASCII and output strings
    # as-is and return unicode strings.
    JSON_AS_ASCII = False
