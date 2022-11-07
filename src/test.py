from smtplib import SMTP
import smtplib
from email.message import Message, EmailMessage

smtp =  SMTP('rbconsult.co.za')
print(smtp.set_debuglevel(1))

try:
    print(smtp.login("webmaster@rbconsult.co.za", "Webmail@RBC2022"))

    smtp.sendmail("webmaster@rbconsult.co.za", "siphomancam2@gmail.com", 
                "Hello there from pyscipt.")
except smtplib.SMTPHeloError as e:
    print(e)

except smtplib.SMTPAuthenticationError as ae:
    print("Incorrect username or password: {}".format(ae))
except smtp.SMTPRecipientsRefused as re:
    print(re)



