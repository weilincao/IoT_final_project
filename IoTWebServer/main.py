# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
import datetime

from flask import Flask, render_template, request, current_app, jsonify
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import storage
import email_sender
import config

app = Flask(__name__)
app.config.from_object(config)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()


def upload_image_file(img):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not img:
        return None

    public_url = storage.upload_file(
        img.read(),
        img.filename,
        img.content_type
    )

    current_app.logger.info(
        'Uploaded file %s as %s.', img.filename, public_url)

    return public_url


def store_time(email, dt):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)


def fetch_times(email, limit):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='visit', ancestor=ancestor)
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times


@app.route('/notify', methods=['POST'])
def notify():
    """Emails all authorized users when motion has been detected"""
    sensor_str = request.macAddr
    img = request.files['photo']
    url = None
    if img is not None:
        url = upload_image_file(img)

    # Create and place a datastore entry in the cloud datastore
    entity = datastore.Entity(key=datastore_client.key('Device', sensor_str, 'motion_event'))
    timestamp = datetime.datetime.now()
    entity.update({
        'timestamp': timestamp,
        'url': url
    })
    datastore_client.put(entity)

    email_sender.send_emails(sensor_str, url)

    return jsonify({'Success': 'Image uploaded to ' + url}), 200


@app.route('/test', methods=['POST'])
def test():
    img = request.files['photo']
    if img is None:
        return jsonify({'Error': 'Image must be named \'photo\''}), 400
    print(img.filename, img.content_type)
    url = upload_image_file(img)

    return jsonify({'Success': 'Image uploaded to ' + url}), 200


@app.route('/')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            store_time(claims['email'], datetime.datetime.now())
            times = fetch_times(claims['email'], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        'index.html',
        user_data=claims, error_message=error_message, times=times)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=1010, debug=True)
# [END gae_python38_render_template]
