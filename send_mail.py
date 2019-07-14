import httplib2
import os
import oauth2client
from oauth2client import client, tools
from oauth2client import file 
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import csv
import codecs
import random

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
APPLICATION_NAME = 'Gmail API Python Send Email'
CLIENT_SECRET_FILE = 'client_secret_ishandutta2007.json'# This file will be in local dir
CREDENTIAL_FILE_NAME = 'gmail-python-email-send_ishandutta2007.json'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, CREDENTIAL_FILE_NAME)
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print(('Storing credentials to ' + credential_path))
    return credentials

def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else:
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print(('Message Id: %s' % message['id']))
        return message
    except errors.HttpError as error:
        print(('An error occurred: %s' % error))
        return "Error"
    return "OK"

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))

    b64_bytes = base64.urlsafe_b64encode(msg.as_bytes())
    b64_string = b64_bytes.decode()
    return {'raw': b64_string}

def createMessageWithAttachment(
    sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients
      attachmentFile: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)

    message.attach(messageA)

    print(("create_message_with_attachment: file:", attachmentFile))
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    with open(attachmentFile, 'rb') as fp:
        if main_type == 'text':
            msg = MIMEText(fp.read(), _subtype=sub_type)
        elif main_type == 'image':
            msg = MIMEImage(fp.read(), _subtype=sub_type)
        elif main_type == 'audio':
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
        else:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    return {'raw': b64_string}

def get_msgHtml(username, fullname, repo_url):
    f = codecs.open("pretrained_model_request_mail_" + str(random.randint(1,2)) + ".html", 'r')
    msgHtml = f.read()
    if fullname is not None:
        msgHtml = msgHtml.replace('[fullname]', fullname.split(' ')[0].title())
    else:
        msgHtml = msgHtml.replace('[fullname]', username.title())
    msgHtml = msgHtml.replace('[repo]', repo_url)
    msgHtml = msgHtml.replace('[sender]', "Ishan")
    return msgHtml

def sendmail(attribute):
    username = attribute[0]
    repo_url = attribute[1]
    fullname = attribute[2]
    email = attribute[3]
    print(('Sending email to %s' % (str(email))))

    to = email
    sender = "you.email"
    subject = "Re:"+repo_url.split('/')[4].replace('-',' ').replace('_',' ').title()
    msgPlain = ""
    msgHtml = get_msgHtml(username, fullname, repo_url)
    SendMessage(sender, to, subject, msgHtml, msgPlain)

def main():
    with open("email-list.csv", "rt") as file:
        msg_reader = csv.reader(file)
        next(msg_reader)
        list(map(lambda x: sendmail(x), msg_reader))

    # # Send message with attachment:
    # SendMessage(sender, to, subject, msgHtml, msgPlain, '/path/to/file.pdf')

if __name__ == '__main__':
    main()
