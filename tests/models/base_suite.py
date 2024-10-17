import copy
import json

import pytest


class BaseSuite:
  @pytest.fixture
  def instance(self):
    pass

  @pytest.fixture
  def model_class(self, instance):
    return type(instance)

  @pytest.fixture
  def resp_body(self, instance):
    return instance.body

  def test_create_succeeds_with_required_attributes(self, model_class,
                                                    resp_body):
    assert isinstance(model_class(resp_body), model_class)

  def test_create_fails_when_missing_required_attributes(self, model_class,
                                                         resp_body):
    for attr in model_class._required:
      bad_resp_body = copy.deepcopy(resp_body)
      del bad_resp_body["record"][attr]
      with pytest.raises(Exception):
        model_class(bad_resp_body)

  def test_as_dict_works(self, instance, resp_body):
    assert instance.as_dict() == resp_body["record"]

  def test_to_json_works(self, instance, resp_body):
    assert json.loads(instance.to_json()) == resp_body["record"]

  def test_to_json_works_with_output_file(self, instance, resp_body, tmp_path):
    path = (tmp_path / "test.json").as_posix()
    instance.to_json(path)
    with open(path) as f:
      assert json.load(f) == resp_body["record"]
