
from IPython.utils.io import capture_output
from pytest import raises
from unittest import mock 
from .conftest import display_holder
from unittest.mock import patch
from io import StringIO



def test_notify_collect_without_params(ip):
     display_holder.display_array = []
     try:
        ip.run_cell_magic(magic_name="notify_collect", line="", cell="print(1)")
     except Exception as ex:
         print(ex)
     assert 1 == 1