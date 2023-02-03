import pytest
from lf_api.auth import Auth
from lf_api.errors import AuthError
import json

class TestAuth:
  def setup_method(self):
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
      with pytest.raises(AuthError) as e:
        token = auth.access_token
