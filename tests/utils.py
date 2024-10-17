from lfapi.models import ListModel, Model


# Model instance assertions
def assert_is_model(obj, model):
  assert issubclass(model, Model)
  assert isinstance(obj, model)
  return obj

def assert_is_list_model(obj, item_class):
  obj = assert_is_model(obj, ListModel)
  assert obj._item_class is item_class
  return obj
