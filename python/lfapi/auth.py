from datetime import datetime, timedelta
from urllib.parse import urljoin

import lfapi.http_utils as http
from lfapi.errors import AuthError, HttpError


class Auth:
  """The authentication object for fetching API access tokens.

  Parameters:
  client_id
    the ID for the app client in use
  client_secret
    the client secret for the app client
  api_host
    the host to send requests to; defaults to DEFAULT_AUTH_HOST

  Attributes:
  access_token
    the token to use to access the API; automatically refreshed upon expiration
  """

  DEFAULT_AUTH_HOST = 'https://auth.listenfirstmedia.com'
  EXP_BUFFER = timedelta(minutes=1)

  def __init__(self, client_id, client_secret, auth_host=None):
    self.client_id = client_id
    self.client_secret = client_secret
    self.auth_host = Auth.DEFAULT_AUTH_HOST if auth_host is None else auth_host
    self._access_token = None
    self._expires_at = None

  def _fetch_access_token(self):
    # Fetch a token from the auth host's token endpoint
    auth_url = urljoin(self.auth_host, '/oauth2/token')
    auth_data = {
      "client_id": self.client_id,
      "client_secret": self.client_secret,
      "grant_type": 'client_credentials',
      "scope": 'api/basic'
    }
    headers = {
      "content-type": 'application/x-www-form-urlencoded'
    }

    try:
      response = http.make_request(http.POST, auth_url,
                                   data=auth_data, headers=headers)
    except HttpError as err:
      raise AuthError(f'Failed to obtain access token: {err}')

    resp_data = response.json()
    if "access_token" not in resp_data:
      raise AuthError('Invalid token response')

    return resp_data


  @property
  def access_token(self):
    if (self._expires_at is None or
        self._expires_at <= datetime.utcnow() + Auth.EXP_BUFFER):
      token_data = self._fetch_access_token()
      self._expires_at = (datetime.utcnow() +
                          timedelta(seconds=token_data["expires_in"]))
      self._access_token = token_data["access_token"]
    return self._access_token
