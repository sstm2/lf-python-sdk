import json
import os

import pytest
from lfapi.auth import Auth
from lfapi.errors import AuthError


class TestAuth:
  def setup_method(self):
    profile_keys = {"API_KEY", "CLIENT_ID", "CLIENT_SECRET"}
    opt_profile_keys = {"API_HOST", "AUTH_HOST", "ACCOUNT_ID"}

    if os.environ.keys() >= profile_keys:  # Read from environment vars
      profile_keys |= opt_profile_keys & os.environ.keys()
      self.profile = {key.lower(): os.environ[key] for key in profile_keys}

    else:  # Read from profile file
      with open('./tests/config/test_profile.json') as f:
        self.profile = json.load(f)

  @pytest.mark.vcr
  def test_access_token_works(self):
    auth = Auth(
      self.profile["client_id"],
      self.profile["client_secret"],
      auth_host=self.profile.get("auth_host")
    )
    token = auth.access_token
    assert isinstance(token, str)
    assert len(token) > 0

  @pytest.mark.vcr
  def test_access_token_fails_correctly(self):
    for auth in [
      # bad client ID
      Auth(self.profile["client_id"][:-1], self.profile["client_secret"]),
      # bad client secret
      Auth(self.profile["client_id"], self.profile["client_secret"][:-1])
    ]:
      with pytest.raises(AuthError):
        auth.access_token
