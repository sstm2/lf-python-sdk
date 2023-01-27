from urllib.parse import urljoin, urlencode
from datetime import datetime, timedelta
import lf_api.http_utils as http
from lf_api.errors import *


class Auth:
  AUTH_HOST = 'https://auth.listenfirstmedia.com'
  EXP_BUFFER = timedelta(minutes=1)

  def __init__(self, client_id, client_secret):
    self.client_id = client_id
    self.client_secret = client_secret
    self._access_token = None
    self._expires_at = None

  def fetch_access_token(self):
    auth_url = urljoin(Auth.AUTH_HOST, '/oauth2/token')
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
      response = http.make_request(http.POST, auth_url, data=auth_data, headers=headers)
    except HttpError as err:
      raise AuthError(f'Failed to obtain access token: {err}')

    resp_data = response.json()
    if "access_token" not in resp_data:
      raise AuthError('Invalid token response')

    return resp_data


  @property
  def access_token(self):
    if self._expires_at is None or self._expires_at <= datetime.utcnow() + Auth.EXP_BUFFER:
      token_data = self.fetch_access_token()
      self._expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
      self._access_token = token_data["access_token"]
    return self._access_token
