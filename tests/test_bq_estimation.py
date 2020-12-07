
from IPython.utils.io import capture_output
from pytest import raises
from unittest import mock 
from .conftest import display_holder
from unittest.mock import patch
from io import StringIO


def test_get_estimated_kb_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_scan 10", cell="100000")
     assert len(display_holder.display_array) == 4
     assert display_holder.display_array[1].data == 'This Query Will Process <span style="color: #ff0000">97.66 KB</span> '
     

def test_get_estimated_mg_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_scan 10", cell="10000000")
     assert len(display_holder.display_array) == 4
     assert display_holder.display_array[1].data == 'This Query Will Process <span style="color: #ff0000">9.54 MB</span> '
     

def test_get_estimated_gb_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_scan 10", cell="1000000000000")
     assert len(display_holder.display_array) == 4
     assert display_holder.display_array[1].data == 'This Query Will Process <span style="color: #ff0000">931.32 GB</span> '

def test_get_estimated_tb_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_scan 10", cell="100000000000000")
     assert len(display_holder.display_array) == 4
     assert display_holder.display_array[1].data == 'This Query Will Process <span style="color: #ff0000">90.95 TB</span> '


def test_get_estimated_too_larg_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_scan 10", cell="10000000000000000000")
     assert len(display_holder.display_array) == 4
     assert display_holder.display_array[1].data == 'This Query Will Process <span style="color: #ff0000">too larg</span> '


def test_get_estimated_cost_less_then_1_dollar_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_cost 10.0", cell="10000000")
     assert len(display_holder.display_array) == 3
     assert display_holder.display_array[2].data == 'And  Cost <span style="color: #7FFF00"> less then 0.001$ </span> '

def test_get_estimated_cost_more_then_5_dollar_for_query(ip):
     display_holder.display_array = []
     ip.run_cell_magic(magic_name="estimate", line="--block_cost 600.0", cell="100000000000000")
     assert len(display_holder.display_array) == 3
     assert display_holder.display_array[2].data == 'And  Cost <span style="color: #7FFF00"> 500.0$ </span> '

def test_estimated_and_block_query_by_price(ip):
     display_holder.display_array = []
     with patch('extra_magics.bq_estimation.get_input', return_value="Y") as fake_out:
          ip.run_cell_magic(magic_name="estimate", line="--block_cost 400.0", cell="100000000000000")
          assert fake_out.call_count == 1
          assert fake_out.call_args[0][0] == 'Query Cost: 500.0$, limit 400.0, run anyway ? Y/N '
     assert len(display_holder.display_array) == 3
     assert display_holder.display_array[2].data == 'And  Cost <span style="color: #7FFF00"> 500.0$ </span> '


def test_estimated_and_non_block_query_by_price(ip):
     display_holder.display_array = []
     with patch('extra_magics.bq_estimation.get_input', return_value="N") as fake_out:
          ip.run_cell_magic(magic_name="estimate", line="--block_cost 400.0", cell="100000000000000")
          assert fake_out.call_count == 1
          assert fake_out.call_args[0][0] == 'Query Cost: 500.0$, limit 400.0, run anyway ? Y/N '
     assert len(display_holder.display_array) == 5
     assert display_holder.display_array[3].data == '<span style="color: #ff0000">Blocked query running</span> '