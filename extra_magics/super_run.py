from IPython.core.getipython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython.core.magic import register_cell_magic,register_line_cell_magic
from sparkmagic.kernels.wrapperkernel.sparkkernelbase import SparkKernelBase
from IPython.core.error import UsageError
from IPython.utils.capture import capture_output
from IPython.core.displaypub import DisplayPublisher
from IPython.core.display import display
from IPython.display import Markdown
import re
import os
import sys
import requests
import errno


@magics_class
class SuperRun(Magics):
    
    IS_BATCH_JOB = os.getenv('IS_BATCH_JOB')
    GITHUB = os.getenv('GITHUB')
    GIT_TOKEN = os.getenv('GIT_TOKEN')
    GIT_REPO = os.getenv('GIT_REPO')

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--debug', help='show printlines',default=False)
    @magic_arguments.argument('--notebook', help='Notbook Path',default=None)
    @magic_arguments.argument('--regex_filter', help='Filter cells with that has the regex as defined',default=None)
    @line_cell_magic
    def super_run(self,line='', cell=None, local_ns=None):
        args = magic_arguments.parse_argstring(self.super_run,line)
        args.notebook = args.notebook.replace("\"",'')
        if args.regex_filter:
            args.regex_filter =  args.regex_filter.replace("\"",'')
        if self.IS_BATCH_JOB == "True":
            args.notebook = self.interactive_mode(args.notebook)
        from nbformat import read
        nb = read(args.notebook, as_version=4)
        if not nb.cells:
            display (Markdown('<span style="color: #7FFF00">External Notebook is empty</span> '))
        else:
            cell_index = 1
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    if args.regex_filter:
                        if re.match(args.regex_filter,cell.source):
                            display (Markdown('Executing cell index: {0}'.format(cell_index)))
                            res = self.handling_issues(get_ipython().kernel,cell.source)
                            if(res == False):
                                raise Exception("you have an error - in the super run!")
                        else:
                            display (Markdown('skipping cell index {0}, not match the pattern {1} ...'.format(cell_index,args.regex_filter)))
                    else:
                        res = self.handling_issues(get_ipython().kernel,cell.source)
                        if(res == False):
                            raise Exception("you have an error - in the super run!")
                else:
                    display (Markdown('skipping non "code" cell, index {0}..'.format(cell_index)))
                cell_index = cell_index + 1

    def handling_issues(self,kernel,source):
        if isinstance(get_ipython().kernel,SparkKernelBase) == True:
            res = kernel.do_execute(source,True)
        else:
            res = kernel.do_execute(source,True).result()
        if res['status'] != 'ok' :
            return False
        else:
            return True

    def interactive_mode(self,path):
        path_ls = path.split("/")
        file_name = path_ls[len(path_ls) - 1]

        insert_flag = False
        repo_path = ""

        for elem in path_ls:
            if elem == self.GITHUB:
                insert_flag = True
                elem = elem + "/master"
            if insert_flag:
                repo_path = repo_path + "/" + elem

        try:
            return self.download_from_git(file_name, repo_path)
        except FileNotFoundError as e:
            print(e)
        except:
            print("error: ", sys.exc_info()[0], sys.exc_info()[1])

    def download_from_git(self,file_name, repo_path):
        try:
            headers = {'Authorization': 'Token {0}'.format(self.GIT_TOKEN)}
            r = requests.get(f'https://raw.githubusercontent.com/{0}{1}'.format(self.GIT_REPO,repo_path), headers=headers)

            if not r.ok:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f'{repo_path}')

            cwd = os.getcwd()

            if not os.path.isdir('./tmp'):
                os.mkdir("tmp")

            path = f'{cwd}/tmp/{file_name}'

            with open(path, 'wb') as f:
                f.write(r.content)

            return path

        except FileNotFoundError:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f'{repo_path}')
        except:
            raise