import sendgrid
from sendgrid.helpers.mail import *
import datetime
import config


def send_emails(sensor_str, img_url):
    email_list = config.AUTHORIZED_USERS
    sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)
    from_email = Email('iothomesecure297007@gmail.com')

    subject = 'Motion Alert! -- ' + datetime.datetime.today().ctime()
    if sensor_str is None:
        sensor_str = 'TEST'
    if img_url is None:
        img_url = 'https://cdn.mos.cms.futurecdn.net/42E9as7NaTaAi4A6JcuFwG-970-80.jpg.webp'  # test image

    html_content = '<h1>Sensor ' + sensor_str + ' detected motion! </h1>'
    html_content += '<img src=\"' + img_url + '\"/>'
    # img = result['photo']
    # img = b64encode(img).decode("utf-8")
    # html_content += '<img src="data:;base64,' + img + '" height="128" width="128"/><br><br>'
    for email in email_list:
        message = Mail(from_email=from_email,
                       to_emails=To(email),
                       subject=subject,
                       html_content=html_content)
        try:
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
    return


send_emails(None, None)
