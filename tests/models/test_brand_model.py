import pytest
from base_suite import BaseSuite

from lfapi.models import Brand


class TestBrand(BaseSuite):
  @pytest.fixture
  def instance(self):
    return Brand({
      "record": {
        "id": 1234,
        "name": "My Brand",
        "type": "STANDARD",
        "created_at": "0000-00-00T00:00:00.000Z",
        "dimensions": {
          "lfm.brand.name": "My Brand"
        }
      }
    })
