import pytest

from lfapi.errors import LfError
from lfapi.models import AnalyticResponse

resp_body = {
  "columns": [
    {
      "id": "lfm.brand_view.id",
      "name": "Brand View ID",
      "class": "DIMENSION",
      "data_type": "INTEGER"
    },
    {
      "id": "lfm.brand.name",
      "name": "Brand Name",
      "class": "DIMENSION",
      "data_type": "STRING"
    },
    {
      "id": "lfm.post_engagement_score.comments_score_v5",
      "name": "Comments",
      "class": "METRIC",
      "data_type": "INTEGER"
    }
  ],
  "records": [
    [
      1234,
      "My Brand",
      1
    ]
  ]
}

def assert_rows_match_resp(rows, label_field):
  assert [list(row.values()) for row in rows] == resp_body["records"]
  for row in rows:
    assert list(row.keys()) == [col[label_field]
                                for col in resp_body["columns"]]

@pytest.fixture
def analytic_response():
  return AnalyticResponse(resp_body)


class TestAnalyticResponse:
  def test_create_succeeds_with_required_attributes(self):
    assert isinstance(AnalyticResponse(resp_body), AnalyticResponse)

  def test_create_fails_when_missing_required_attributes(self):
    with pytest.raises(Exception):
      AnalyticResponse({"columns": resp_body["columns"]})

  def test_create_handles_label_mode_param(self):
    assert isinstance(AnalyticResponse(resp_body, label_mode="id"),
                      AnalyticResponse)
    assert isinstance(AnalyticResponse(resp_body, label_mode="name"),
                      AnalyticResponse)
    with pytest.raises(LfError):
        AnalyticResponse(resp_body, label_mode="other")

  def test_as_list(self, analytic_response):
    # check default behavior
    assert_rows_match_resp(analytic_response.as_list(), "id")
    analytic_response.label_mode = "id"
    # check explicit id setting
    assert_rows_match_resp(analytic_response.as_list(), "id")
    # check name setting
    analytic_response.label_mode = "name"
    assert_rows_match_resp(analytic_response.as_list(), "name")

  def test_as_dict_list(self, analytic_response):
    # check default behavior
    assert_rows_match_resp(analytic_response.as_dict_list(), "id")
    analytic_response.label_mode = "id"
    # check explicit id setting
    assert_rows_match_resp(analytic_response.as_dict_list(), "id")
    # check name setting
    analytic_response.label_mode = "name"
    assert_rows_match_resp(analytic_response.as_dict_list(), "name")

  def test_add_works(self, analytic_response):
    ar1 = analytic_response
    ar2 = AnalyticResponse(resp_body)
    ar_sum = ar1 + ar2
    assert isinstance(ar_sum, AnalyticResponse)
    assert len(ar_sum) == len(ar1) + len(ar2)
    assert ar_sum.as_list() == ar1.as_list() + ar2.as_list()

  def test_add_rejects_incompatible_ops(self, analytic_response):
    ar1 = analytic_response
    ar2 = AnalyticResponse({
      "columns": resp_body["columns"][:-1],
      "records": [rec[:-1] for rec in resp_body["records"]]
    })
    with pytest.raises(LfError):
      ar1 + ar2
