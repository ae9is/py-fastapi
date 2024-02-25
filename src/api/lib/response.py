import json
import fastapi


def generate_response(body={}, status=200, headers: dict[str, str] = {}):
  formatted = json.dumps(body)
  cors = {'Access-Control-Allow-Origin': '*'}
  content_type = {'Content-Type': 'application/json'}
  with_preset = cors | content_type | headers
  response = fastapi.Response(content=formatted, status_code=status, headers=with_preset, media_type=content_type)
  return response
