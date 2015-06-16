from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# emailTo, emailCc, emailBcc: lists of email addresses
# emailSubject, emailBody: strings
def sendEmail(emailTo, emailCc, emailBcc, emailSubject, text, html):
    
    # Send the message via Gmail's SMTP server
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(email_username, email_password)
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = emailSubject
        msg['From'] = global_passed_vars['website_name'] + "<" + email_username + ">"
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
            
        server.sendmail(email_username, emailTo + emailCc + emailBcc, msg.as_string())
        server.quit()
        return True
    except:
        return False