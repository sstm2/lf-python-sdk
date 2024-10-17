import pytest
from base_suite import BaseSuite

from lfapi.models import Dataset


class TestBrandSet(BaseSuite):
  @pytest.fixture
  def instance(self):
    return Dataset({
      "record": {
        "id": "dataset_test",
        "name": "Test Fields",
        "description": "Test dataset.",
        "analysis_type": "BRAND",
        "dataset_type": "ANALYTIC"
      }
    })
