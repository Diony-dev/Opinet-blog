import os

class DevelopmentConfig():
    DEBUG = True
    PORT = 8000


class ProductionConfig():
    DEBUG = False
    PORT = os.environ.get('PORT', 5000)


config = {
    'develop': DevelopmentConfig,
    'production': ProductionConfig,
}