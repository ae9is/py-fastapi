import requests as req


def test_healthz(port=5000):
  url = f'http://localhost:{port}/v1/healthz'
  response: req.Response = req.request('GET', url)
  assert response.status_code == 200
