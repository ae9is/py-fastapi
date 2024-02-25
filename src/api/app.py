import sys

import fastapi as fast
import fastapi_cloudauth as fastauth

from api.lib.config import AWS_REGION, COGNITO_APPCLIENT_ID, COGNITO_AUTH_USER_SCOPE, COGNITO_USERPOOL_ID
from api.lib.response import generate_response as r
from api.lib.logger import debug


app = fast.FastAPI()
protected = fast.APIRouter()
auth = fastauth.Cognito(
  region=AWS_REGION,
  userPoolId=COGNITO_USERPOOL_ID,
  client_id=COGNITO_APPCLIENT_ID,
  scope_key='scope',
)
PROTECTED = [fast.Depends(auth.scope([COGNITO_AUTH_USER_SCOPE]))]


@app.get('/v1/healthz', tags=['healthz'])
def healthz():
  return r('OK')


@protected.get('/v1/torch/version', tags=['torch'])
@protected.post('/v1/torch/version', tags=['torch'])
async def torchversion() -> fast.Response:
  debug(f'Using python {sys.version}')
  debug('Trying to load torch...')
  import torch

  version = torch.__version__
  cuda = {
    'version': torch.version.cuda,
    'available': torch.cuda.is_available(),
  }
  body = {
    '__version__': version,
    'cuda': cuda,
  }
  return r(body)


# Router must be included after all router definitions, if included in same file as definitions
app.include_router(protected, dependencies=PROTECTED)


if __name__ == '__main__':
  import uvicorn

  uvicorn.run(app, host='0.0.0.0', port=5000)
