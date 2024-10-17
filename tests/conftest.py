import os

import pytest

from lfapi.client import Client


@pytest.fixture(scope="session")
def client():
  profile_keys = {"API_KEY", "CLIENT_ID", "CLIENT_SECRET"}
  opt_profile_keys = {"API_HOST", "AUTH_HOST", "ACCOUNT_ID"}

  if os.environ.keys() >= profile_keys:  # Read from environment vars
    profile_keys |= opt_profile_keys & os.environ.keys()
    profile = {key.lower(): os.environ[key] for key in profile_keys}
    return Client.from_dict(profile)

  else:  # Read from profile file
    return Client.load('./tests/config/test_profile.json')

@pytest.fixture(scope="session")
def brand_id():
  brand_id = os.environ.get("BRAND_ID")
  if brand_id is not None:
    return int(brand_id)
  raise "Missing BRAND_ID environment variable"

@pytest.fixture(scope="session")
def brand_set_id():
  return 4626  # My Brands

@pytest.fixture(scope="session")
def client_context():
  return 'lfapi pytest client context'

@pytest.fixture(scope="session")
def fetch_params(brand_id):
  return {
    "dataset_id": 'dataset_brand_listenfirst',
    "start_date": '2022-07-10',
    "end_date": '2022-08-10',
    "group_by": [
      'lfm.brand_view.id'
    ],
    "metrics": [
      'lfm.post_engagement_score.comments_score_v5'
    ],
    "meta_dimensions": [
      'lfm.brand.name'
    ],
    "filters": [
      {
        "field": 'lfm.brand_view.id',
        "operator": 'IN',
        "values": [
          brand_id
        ]
      }
    ]
  }
