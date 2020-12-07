from IPython.testing.globalipapp import start_ipython
import pytest
from unittest import mock 
import sys
from .mocks import *


display_holder = DisplayHolder()

@pytest.fixture(scope="session")
def session_ip():
    __initTestMocks()
    return start_ipython()


@pytest.fixture(scope="function")
def ip(session_ip):
    session_ip.run_line_magic(magic_name="load_ext", line="extra_magics")
    yield session_ip
    session_ip.run_line_magic(magic_name="unload_ext", line="extra_magics")
    session_ip.run_line_magic(magic_name="reset", line="-f")


def __initTestMocks():
    ## Mocking Goolgle Cloud Bigquwey
    module = type(sys)('google.cloud.bigquery')
    module.Client = ClientMock
    module.QueryJobConfig = QueryJobConfig
    sys.modules['google.cloud.bigquery'] = module
    import IPython.core.display
    IPython.core.display.display = displyMocker(display_holder)
    return display_holder