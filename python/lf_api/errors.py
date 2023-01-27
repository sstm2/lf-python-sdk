class LfError(Exception): pass

class HttpError(LfError):
  def __init__(self, response):
    req_method = response.request.method
    url = response.url
    status_code = response.status_code
    reason = response.reason
    json = response.json()
    msg = f'{req_method} request to {url} failed with {status_code} {reason}: {json}'
    super().__init__(msg)

class BadRequest(HttpError): pass
class Unauthorized(HttpError): pass
class RecordNotFound(HttpError): pass
class RequestInvalid(HttpError): pass
class QuotaSurpassed(HttpError): pass
class LfServerError(HttpError): pass

class AuthError(LfError): pass
