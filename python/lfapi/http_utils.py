import requests
from lfapi.errors import (BadRequest, HttpError, QuotaSurpassed,
                          RecordNotFound, RequestInvalid, ServerError,
                          Unauthorized)

POST = requests.post
GET = requests.get

def make_request(method, url, **request_args):
  """Make HTTP requests."""
  response = method(url, **request_args)
  status = response.status_code

  if status == 400:
    raise BadRequest(response)
  if status == 401:
    raise Unauthorized(response)
  if status == 404:
    raise RecordNotFound(response)
  if status == 422:
    raise RequestInvalid(response)
  if status == 429:
    raise QuotaSurpassed(response)
  if status >= 500:
    raise ServerError(response)
  if not 200 <= status < 300:
    raise HttpError(response)

  return response
