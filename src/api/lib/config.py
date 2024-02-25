import os

from dotenv import load_dotenv  # , dotenv_values

load_dotenv(dotenv_path='env')
# print(dotenv_values(dotenv_path='env'))

PYTHON_ENV = os.environ.get('PYTHON_ENV', 'production')
DEV = PYTHON_ENV == 'development'

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
COGNITO_USERPOOL_ID = os.environ.get('COGNITO_USERPOOL_ID', '')
COGNITO_APPCLIENT_ID = os.environ.get('COGNITO_APPCLIENT_ID', '')
COGNITO_AUTH_USER_SCOPE = os.environ.get('COGNITO_AUTH_USER_SCOPE', 'pyapi/user')
