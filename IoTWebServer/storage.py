from __future__ import absolute_import

import datetime
import os

from flask import current_app
from google.cloud import storage
import six
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename


def _check_extension(filename, allowed_extensions):
    file, ext = os.path.splitext(filename)
    if ext.replace('.', '') not in allowed_extensions:
        raise BadRequest(
            '{0} has an invalid name or extension'.format(filename))


def _safe_filename(filename):
    """
    Generates a safe filename that is unlikely to collide with existing
    objects in Google Cloud Storage.
    ``filename.ext`` is transformed into ``filename-YYYY-MM-DD-HHMMSS.ext``
    """
    filename = secure_filename(filename)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, date, extension)


def upload_file(file_stream, filename, content_type):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """
    _check_extension(filename, current_app.config['ALLOWED_EXTENSIONS'])
    filename = _safe_filename(filename)

    client = storage.Client(project=current_app.config['PROJECT_ID'])
    bucket = client.bucket(current_app.config['CLOUD_STORAGE_BUCKET'])
    blob = bucket.blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type)
    # Ensure the file is publicly readable.
    blob.make_public()

    url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    return url
