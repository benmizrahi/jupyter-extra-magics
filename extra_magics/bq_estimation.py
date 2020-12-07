from IPython.core.getipython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython.core.magic import register_cell_magic,register_line_cell_magic
from IPython.core.error import UsageError
from IPython.utils.capture import capture_output
from IPython.core.display import display
from IPython.display import Markdown
import os
import time
import smtplib
from google.cloud import bigquery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .cell_execution import  execute_cell_get_output


def get_input(text):
    return input(text)


@magics_class
class BQEstimation(Magics):

    SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--block_cost', help='If esitmated query cost is larger then @param$ dont run')
    @magic_arguments.argument('--block_scan', help='If esitmated query scan is larger then @param gb dont run')
    @magic_arguments.argument('--dry-run',default=True, help='do the cell contains %%bigquery magic ?')
    @line_cell_magic
    def estimate(self,line= '', cell=None, local_ns=None):
        args = magic_arguments.parse_argstring(self.estimate,line)
        contains_execution = "%%bigquery" in cell
        query =  cell.replace("%%bigquery","")
        display(Markdown('Running estimation ...'))
        client = bigquery.Client()
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        query_job = client.query((query),job_config=job_config,)
            
        query_cost = self.__calculate_pricing(query_job.total_bytes_processed)
        query_scan = self.__get_size(query_job.total_bytes_processed)

        query_cost_string = str(query_cost) + "$"
        if query_cost < 0.001:
            query_cost_string = "less then 0.001$"

        display (Markdown('This Query Will Process <span style="color: #ff0000">{}</span> '.format(query_scan)))
        display (Markdown('And  Cost <span style="color: #7FFF00"> {} </span> '.format(query_cost_string)))

        run = "Y"
        if args.block_cost or args.block_scan and contains_execution :
            if args.block_cost is not None and query_cost >  float(args.block_cost):
                run = get_input('Query Cost: {0}, limit {1}, run anyway ? Y/N '.format(query_cost_string,args.block_cost))
            elif args.block_scan is not None and query_scan > float(args.block_scan):
                run = get_input('run ? Y/N ')
        else:
            if contains_execution: 
                return execute_cell_get_output(get_ipython(),line,cell,local_ns)
            else:
                display (Markdown('<span style="color: #ff0000">Done</span> '))
        if(run.upper() == "Y"):
            return execute_cell_get_output(get_ipython(),line,cell,local_ns)
        else:
            display (Markdown('<span style="color: #ff0000">Blocked query running</span> '))
            display (Markdown('<span style="color: #ff0000">Done</span> '))

    def __calculate_pricing(self,total_bytes_processed):
        bytes_in_tb = 1000000000000
        return round((total_bytes_processed * 5) / bytes_in_tb,3)

    def __get_size(self,size_in_bytes): 
        index = 0
        while size_in_bytes >= 1024:
            size_in_bytes /= 1024
            index += 1
        try:
            return f'{round(size_in_bytes,2)} {self.SIZE_UNITS[index]}'
        except IndexError:
            return 'too larg'