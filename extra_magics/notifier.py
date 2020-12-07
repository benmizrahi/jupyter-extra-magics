from IPython.core.getipython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython.core.magic import register_cell_magic,register_line_cell_magic
from IPython.core.error import UsageError
from IPython.utils.capture import capture_output
from IPython.core.displaypub import DisplayPublisher
from IPython.core.display import display
from IPython.display import Markdown
import os
import smtplib
from slack import WebClient
from slack.errors import SlackApiError
from pandas import DataFrame
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from .cell_execution import  execute_cell_get_output
from datetime import datetime
import pytz
import uuid


class Attachment(object):

    def __init__(self,type,content):
        self.type = type
        self.content = content
    
    def get_type(self):
        return self.type
    
    def get_content(self):
        return self.content

@magics_class
class Notifier(Magics):

    slack_client_token = os.getenv('SLACK_API_TOKEN')
    email_pass = os.getenv('EMAIL_PASS')
    email_user = os.getenv('EMAIL_USER')
    env = os.getenv('ENV')

    collector = {}

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--kind', help='Kind of notification EMAIL|SLACK')
    @magic_arguments.argument('--destination', '-t', help='where to send the message to ? EMAIL|CHANNEL (test@gmail.com,test2@gmail.com)')
    @magic_arguments.argument('--header', help='Header',default='My Header for Notifications')
    @magic_arguments.argument('--body', help='Message Body',default='')
    @magic_arguments.argument('--debug', help='show printlines',default=False)
    @line_cell_magic
    def notify_collect(self,line='', cell=None, local_ns=None):
        args = magic_arguments.parse_argstring(self.notify_collect,line)
        self.__validate_args(args) #validate params
        original_out =  execute_cell_get_output(get_ipython(),line,cell,local_ns)
        attachment = None
        if original_out is not None:
            if hasattr(original_out,"to_html"):
                attachment = Attachment(type="table",content=self.build_final_html(args.body.replace("\"",""),original_out.to_html(index=False,bold_rows=True,justify="left")))
            elif original_out.__class__.__name__ == 'AxesSubplot':
                image_uuid = uuid.uuid1()
                original_out.figure.savefig('/tmp/{0}.png'.format(image_uuid))
                attachment = Attachment(type="image", content= { 'path':'/tmp/{0}.png'.format(image_uuid),'id':image_uuid,'message':args.body.replace("\"","") })
            else:
                attachment = Attachment(type="text", content= str(original_out))
            mail_keys = args.kind + '_' + args.destination.replace("\"","") + '_' + args.header.replace("\"","") 
            if mail_keys in self.collector:
                self.collector[mail_keys].append(attachment)
            else:
                self.collector[mail_keys] = []
                self.collector[mail_keys].append(attachment)

        return original_out

    def build_final_html(self,header,html_table):
        out = self.build_output(header)
        out += html_table.replace("""<thead>""",""" <thead style="font-size: 16px;text-align:left;color: white;background: #007d2c">""").replace("<td","""<td style="text-align:left;padding:8px;" """)      
        return out

    def build_output(self,header):
        return """<h1 class="tableheader">{0}</h1>""".format(header)

    @line_cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--show_env', help='show env header in email',default='True')
    def notify(self,line='', cell=None, local_ns=None):
        args = magic_arguments.parse_argstring(self.notify,line)
        if len(self.collector) == 0:
            raise Exception("didn't genther any EMAIL in notebook, please use %%notify_collect first")
        for params in self.collector:
            kind, destination, header = params.split("_")
            if kind == "SLACK":
                self.send_slack(destination,self.collector[params])
            elif kind == "EMAIL":
                self.send_email(self.collector[params],header,destination,args.show_env)
        display (Markdown('<span style="color: #7FFF00">Email Sent!</span> '))
        self.collector = {}

    def send_email(self,attachments, subject, emails,show_env):
        msg = MIMEMultipart('alternative')
        if show_env == 'True':
            msg['Subject'] = "[{0}] ".format(self.env.upper()) + "[{0}]".format(subject)
        else:
            msg['Subject'] = "[{0}]".format(subject)
        msg["To"] = emails
        self.build_email_from_attachmet_list(attachments,msg)
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.ehlo()
        mail.login(self.email_user, self.email_pass)
        mail.sendmail('BI Notifications', msg["To"].split(","), msg.as_string())
        mail.quit()
    
    def build_email_from_attachmet_list(self,attachments,msg):
        image_number = 0
        html = ""
        for attachment in attachments:
            if attachment.get_type() == 'table':
                html += attachment.get_content() + "</br>"
            elif attachment.get_type() == 'image':
                with open(attachment.get_content()['path'], 'rb') as f:
                    html +=  '<h1>{header}</h1> <img src="cid:image_id_{cid}">'.format(cid=str(image_number),header=attachment.get_content()['message'])
                    msg_image = MIMEImage(f.read(),name=os.path.basename(attachment.get_content()['path']))
                    msg.attach(msg_image)
                    msg_image.add_header('Content-ID', '<{0}>'.format("image_id_{0}".format(str(image_number))))
                    image_number = image_number + 1
            else:
                html += "<p>{0}</p>".format(attachment.get_content())
        html_part = MIMEText(html,'html', 'utf-8')
        msg.attach(html_part)

    def send_slack(self,destination,body):
        try:
            response = WebClient(token=self.slack_client_token).chat_postMessage(
                channel='{0}'.format(destination),
                text="{0}".format(body))
            assert response["message"]["text"] == body
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            print(f"Got an error: {e.response['error']}")

    def __validate_args(self,args):
        if not args.kind or ("SLACK" not in args.kind and "EMAIL" not in args.kind) :
            raise Exception("Kind should be SLACK or EMAIL")
        if not args.destination:
            raise  Exception("destination shouln't is empty")
        if not args.header:
            raise Exception("header should be defined")