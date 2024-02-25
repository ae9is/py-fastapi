import requests as req
import packaging.version as vers

from lib.auth import get_token


def test_torch(port=5000):
  """
  Test /torch/version

  Args:
    port: Port that endpoint is at
  """
  url = f'http://localhost:{port}/v1/torch/version'
  token = get_token()
  headers = {'Authorization': f'{token.token_type} {token.access_token}', 'Content-Type': 'application/json'}
  payload = None
  response: req.Response = req.request('POST', url, headers=headers, data=payload)
  assert response.status_code == 200
  output = response.json() or {}
  print(f'response: {output}')
  pytorch_version = output['__version__']
  current_version = vers.parse(pytorch_version)
  min_version = vers.parse('2.2.0')
  assert current_version >= min_version


if __name__ == '__main__':
  print('Testing /torch/version ...')
  test_torch()
  print('Done testing')
