class LfError(Exception):
  """Base exception for lf_api."""
  pass


class HttpError(LfError):
  """Exception for HTTP request failures.

  Parameters:
  response
    the response from the failed HTTP request
  """

  def __init__(self, response):
    req_method = response.request.method
    url = response.url
    status_code = response.status_code
    reason = response.reason
    json = response.json()
    msg = f'{req_method} request to {url} failed with {status_code} {reason}: {json}'
    super().__init__(msg)

class BadRequest(HttpError):
  """Exception for 400 HTTP failures."""
  pass

class Unauthorized(HttpError):
  """Exception for 401 HTTP failures."""
  pass

class RecordNotFound(HttpError):
  """Exception for 404 HTTP failures."""
  pass

class RequestInvalid(HttpError):
  """Exception for 422 HTTP failures."""
  pass

class QuotaSurpassed(HttpError):
  """Exception for 429 HTTP failures."""
  pass

class ServerError(HttpError):
  """Exception for 5xx HTTP failures."""
  pass


class AuthError(LfError):
  """Exception for authentication related failures."""
  pass
