from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# login_name: string, the email used to send out the emails
# login_pwd: string, the password of the email used to send out the emails
# fromName: string, how the 'from' appears in the email (e.g., "Talk2Me")
# emailTo, emailCc, emailBcc: lists of email addresses
# emailSubject, emailBody: strings
def sendEmail(login_name, login_pwd, fromName, emailTo, emailCc, emailBcc, emailSubject, text, html):
    
    # Send the message via Gmail's SMTP server
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(login_name, login_pwd)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = emailSubject
        msg['From'] = fromName + "<" + login_name + ">"
        msg['To'] = ",".join(emailTo)
        msg['Cc'] = ",".join(emailCc)
        msg['Bcc'] = ",".join(emailBcc)

        # Create an HTML and alternate plain text version
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
            
        server.sendmail(login_name, emailTo + emailCc + emailBcc, msg.as_string())
        server.quit()
        return True
    except:
        return False