import pytest
from base_suite import BaseSuite

from lfapi.models import BrandSet


class TestBrandSet(BaseSuite):
  @pytest.fixture
  def instance(self):
    return BrandSet({
      "record": {
        "id": 4626,
        "name": "My Brands",
        "created_at": "2020-06-05T02:17:52.615Z",
        "updated_at": "2020-06-05T02:17:52.615Z"
      }
    })
