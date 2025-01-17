import os
import sys

from sea.utils import import_string
from sea.local import Proxy
from sea.signals import post_ready

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_app = None


def create_app(root_path=None):
    global _app
    if _app is not None:
        return _app

    if root_path is None:
        root_path = os.getcwd()
    sys.path.append(root_path)
    sys.path.append(os.path.join(root_path, "protos"))

    env = os.environ.get("SEA_ENV", "development")
    config = import_string("configs.{}".format(env))

    app_class = import_string("app:App")
    _app = app_class(root_path, env=env)
    _app.config.from_object(config)
    # only filter default configurations
    _app.config.load_config_from_env()

    _app.load_middlewares()
    _app.load_extensions_in_module(import_string("app.extensions"))
    _app.load_servicers_in_module(import_string("app.servicers"))

    _app.ready()
    post_ready.send(_app)

    return _app


current_app = Proxy(lambda: _app)
