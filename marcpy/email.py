import os
import sys
import zipfile
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from marcpy.keyring_wrappers import key_get

# fromEmail = "marc_gis@marc.org"
# toEmails = 'jpeterson@marc.org'
# subject = 'test email'
# body = 'This is a test.\nThis is line2.'

def sendEmail(fromEmail, toEmails, subject, body):
    """Send Email
    
    Send an Email with Python.
    This function is modified for Python 3 from an old local MARC script found 
    in X:\\Tools\\Scripting\\Admin\\rsMailPython.py.
    http://naelshiab.com/tutorial-send-email-python/
    
    Parameters
    ----------
    fromEmail : str
        Email address you want to send from. it must be in your Window's 
        Credential Manager as ':EMAIL:<fromEmail>'
    toEmail : str, list
        To what emails should the message be sent?
    subject : str
        Subject for email.
    body : str
        Body for email.
        
    Return
    ------
    None
    """
    
    #Get stored email password
    fromEmailPwd = key_get(serviceName="EMAIL", userName = fromEmail)
    
    #Set up smtplib object
    s = smtplib.SMTP('smtp.office365.com')
    s.starttls()
    s.login(fromEmail, fromEmailPwd)
    
    #set up message precursers
    sender = fromEmail
    #Enforce to is a list
    if isinstance(toEmails, str):
        toEmails = [toEmails]
    recipients = toEmails
    body = body
    
    #Create message object
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(toEmails)
    msg.attach(MIMEText(body,'plain'))
    
    #Send email
    s.sendmail(sender, recipients, msg.as_string())
    
    #Close object
    s.quit()


def main(argv=None):
    sendEmail(fromEmail='<email>', toEmails=['<email1>', '<email2>'], subject = 'Subject Heading', body='This is my body.\nThis is line 2.')

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
