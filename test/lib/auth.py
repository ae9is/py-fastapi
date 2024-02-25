import os
import sys

sys.path.append(os.path.abspath('./src/api'))

import requests as req

from api.lib.config import (
  COGNITO_APPCLIENT_ID as CLIENT_ID,
  COGNITO_AUTH_USER_SCOPE as SCOPE,
  AWS_REGION,
)


COGNITO_DOMAIN = os.environ.get('COGNITO_DOMAIN', '')
CLIENT_SECRET = os.environ.get('COGNITO_SECRET', '')
TOKEN_URL = f'https://{COGNITO_DOMAIN}.auth.{AWS_REGION}.amazoncognito.com/oauth2/token'


class Token:
  def __init__(
    self,
    *,
    access_token: str = None,
    expires_in: int = 3600,
    token_type: str = 'Bearer',
  ):
    self.access_token = access_token
    self.expires_in = expires_in
    self.token_type = token_type


def get_token() -> Token:
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  payload = f'grant_type=client_credentials&client_id={CLIENT_ID}&scope={SCOPE}&client_secret={CLIENT_SECRET}'
  response: req.Response = req.request('POST', TOKEN_URL, headers=headers, data=payload)
  token = Token(**response.json())
  return token
