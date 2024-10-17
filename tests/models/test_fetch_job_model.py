import pytest
from base_suite import BaseSuite
from utils import assert_is_model

from lfapi.errors import LfError
from lfapi.models import AnalyticResponse, NoClientError

VERBOSE_ATTRS = ["query_cost", "fetch_params", "max_rows"]

def assert_is_verbose(fetch_job):
  for attr in VERBOSE_ATTRS:
    assert hasattr(fetch_job, attr)


class TestFetchJobModel(BaseSuite):
  @pytest.fixture
  def instance(self, client, fetch_params):
    return client.create_fetch_job(json={"fetch_params": fetch_params})

  # analytics methods
  @pytest.mark.vcr
  def test_update_with_client(self, instance):
    instance.update()
    assert_is_verbose(instance)

  def test_update_without_client(self, instance):
    setattr(instance, "client", None)
    with pytest.raises(NoClientError):
      instance.update()

  @pytest.mark.vcr
  def test_poll_with_client(self, instance):
    instance.poll()
    assert_is_verbose(instance)

    assert instance.state == "completed" and hasattr(instance, "page_urls")

  def test_poll_without_client(self, instance):
    setattr(instance, "client", None)
    with pytest.raises(NoClientError):
      instance.poll()

  @pytest.mark.vcr
  def test_download_pages(self, instance):
    with pytest.raises(LfError):
      instance.download_pages()
    instance.poll()
    for page in instance.download_pages():
      assert_is_model(page, AnalyticResponse)
