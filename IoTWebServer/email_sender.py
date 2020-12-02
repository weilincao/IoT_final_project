import sendgrid
from sendgrid.helpers.mail import *
import datetime
import config


def send_emails(sensor_str, img_url):
    email_list = config.AUTHORIZED_USERS
    sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)
    email_from = Email('iothomesecure297007@gmail.com')

    email_subject = 'Motion Alert! -- ' + datetime.datetime.today().ctime()
    if sensor_str is None:
        sensor_str = 'TEST'
    if img_url is None:
        img_url = 'https://cdn.mos.cms.futurecdn.net/42E9as7NaTaAi4A6JcuFwG-970-80.jpg.webp'  # test image

    for i in range(0, len(config.AUTHORIZED_DEVICES)):  # Could possibly be replaced with a dynamic naming system
        if sensor_str == config.AUTHORIZED_DEVICES[i]:
            sensor_str = config.AUTHORIZED_DEVICE_NAMES[i]
            break

    email_body = '<h1>Sensor ' + sensor_str + ' detected motion! </h1>'
    email_body += '<img src=\"' + img_url + '\"/>'
    # img = result['photo']
    # img = b64encode(img).decode("utf-8")
    # html_content += '<img src="data:;base64,' + img + '" height="128" width="128"/><br><br>'
    for email in email_list:
        message = Mail(from_email=email_from,
                       to_emails=To(email),
                       subject=email_subject,
                       html_content=email_body)
        try:
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
    return
