import time
from math import log10

import requests
from lfapi.errors import (BadRequest, HttpError, LfError, QuotaSurpassed,
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

def retry(f, max_tries=3, max_wait_time=7200, delay=1, retry_condition=None):
  """Retry function execution.

  Arguments:
  f
    the function to attempt to execute
  max_tries
    the maximum number of attempts; default 3
  max_wait_time
    the maximum total wait time across all attempts; default 2 hours
  delay
    the initial time to wait between attempts; default 1 second
  retry_condition
    if specified, determines whether the result from f is sufficient to cease
    execution attempts
  """
  assert max_tries >= 1
  assert max_wait_time > 0
  assert delay >= 0

  def _f(*args, **kwargs):
    nonlocal max_tries, max_wait_time, delay, retry_condition

    tries = 0
    start_time = time.time()
    while time.time() - start_time < max_wait_time and tries < max_tries:
      if tries > 0:
        # Apply logarithmic backoff and sleep between iterations
        delay += log10(tries)
        time.sleep(delay)

      try:
        # Attempt execution and check result against retry_condition
        result = f(*args, **kwargs)
        if retry_condition is None or not retry_condition(result):
          return result
      except HttpError as err:
        # Allow max_tries HttpErrors
        if tries >= max_tries - 1:
          raise err

      # Iterate
      tries += 1

    raise LfError("Exceeded max wait time; exiting.")

  return _f
