import pytest
from base_suite import BaseSuite

from lfapi.models import ScheduleConfig


class TestScheduleConfigModel(BaseSuite):
  @pytest.fixture
  def instance(self, client_context):
      return ScheduleConfig({"record": {
        "id": 1234,
        "state": "created",
        "created_at": "2024-10-17T00:00:00.000Z",
        "updated_at": "2024-10-17T00:00:00.000Z",
        "client_context": client_context
      }})
