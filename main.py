from apps import create_app
from decouple import config
from apps.config import config_dict
from apps.backend.services.tasks import fetch_data
from apps.backend.services.complexity_score import ComplexityAnalyzer

# WARNING: Don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
    # a = ComplexityAnalyzer()
    # a.save_complexity_score()
    # fetch_data.delay()

