import importlib
import importlib.util
import sys
from functools import wraps


def safe_import(dep_name):
  try:  # fails for submodules, can treat it the same as a None
    if importlib.util.find_spec(dep_name) is None:
      return
    return importlib.import_module(dep_name)
  except ModuleNotFoundError:
    return

def depends_on(dep_name):
  def depends_on_decorator(func):
    @wraps(func)
    def _func(*args, **kwargs):
      if dep_name not in sys.modules:
        raise NotImplementedError(f'{dep_name} is not installed')

      return func(*args, **kwargs)

    return _func

  return depends_on_decorator
