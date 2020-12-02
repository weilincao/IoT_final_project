import sendgrid
from sendgrid.helpers.mail import *
import datetime
import config


def send_emails(sensor_str, img_url):
    email_list = config.AUTHORIZED_USERS

    subject = 'Motion Alert! -- ' + datetime.date.today().isoformat()
    if sensor_str is None:
        sensor_str = 'TEST'

    for email in email_list:

        html_content = '<strong>Motion was detected by sensor ' + sensor_str + '!</strong><br><br>'
        # img = result['photo']
        # img = b64encode(img).decode("utf-8")
        # html_content += '<img src="data:;base64,' + img + '" height="128" width="128"/><br><br>'

        html_content += '<br><br>Happy viewing!<br><strong>DestQuest</strong>'

        message = Mail(from_email='noreply@destquest.appspotmail.com',
                       to_emails=email,
                       subject=subject,
                       html_content=html_content)
        try:
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
    return
