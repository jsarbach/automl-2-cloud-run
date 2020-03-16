from base64 import b64decode, b64encode
from flask import Flask, render_template, request
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from os import environ
import requests
from time import sleep


def get_secret(name, retry=5):
    """
    Requests secret from Secret Manager.

    :param name: name of secret (str)
    :param retry: number of retries (int)
    :return: secret value (str)
    """

    service = build('secretmanager', 'v1beta1', cache_discovery=False)

    response = None
    wait = retry
    while response is None:
        try:
            response = service.projects().secrets().versions().access(
                name='projects/{}/secrets/{}/versions/latest'.format(PROJECT_ID, name)).execute()
        except Exception as e:
            if wait:
                sleep(2 ** (retry - wait))
                wait -= 1
            else:
                raise e

    return b64decode(response['payload']['data']).decode()


def get_token(service_account_info, target_audience):
    """
    Creates an ID token.

    :param service_account_info: service account key info (dict)
    :param target_audience: URL of called service (str)
    :return: ID token (str)
    """

    cred = service_account.IDTokenCredentials.from_service_account_info(service_account_info, target_audience=target_audience)
    cred.refresh(Request())
    return cred.token


def predict_image_labels(image, url, service_account_info=None):
    """
    Performs image classification using a RESTful API.

    :param image: image file to be processed (File object)
    :param url: model endpoint (str)
    :param service_account_info: service account key (dict)
    :return: recognised objects and error (tuple of (list of dict(labels, scores)), str)
    """

    payload = {
        'instances': [
            {
                'image_bytes': {'b64': b64encode(image.read()).decode('utf-8')},
                'key': image.name
            }
        ]
    }
    jwt = get_token(service_account_info, url) if service_account_info is not None else None

    response = requests.post(url, headers={'Authorization': f'bearer {jwt}'} if jwt is not None else {}, data=json.dumps(payload))
    response = json.loads(response.content)
    predictions = response.get('predictions', [{}])[0]
    return [
        {
            'label': label,
            'score': '{:.1%}'.format(score)
        } for label, score in zip(predictions.get('labels', []), predictions.get('scores', []))
    ], response.get('error')


# get environment variables (set by GAE or in app.yaml)
PROJECT_ID = environ.get('GOOGLE_CLOUD_PROJECT')
SECRET_NAME = environ.get('SECRET_NAME')
SERVICE_URL = environ.get('SERVICE_URL')

# retrieve service account info from Secret Manager
service_account_info = json.loads(get_secret(SECRET_NAME))

# instantiate Flask app
app = Flask(__name__)


# Flask routes
@app.route('/', methods=['GET', 'POST'])
def coffee_classifier():
    img_src = ''
    predictions = []

    if request.method == 'POST':
        file = request.files.get('image')
        if file is not None:
            img_b64 = b64encode(file.read()).decode()
            file.seek(0)  # rewind file pointer
            img_src = 'data:{};base64,{}'.format(file.content_type, img_b64)
            predictions, _ = predict_image_labels(file, SERVICE_URL, service_account_info)
            # sort by score
            order = sorted(range(len(predictions)), key=lambda k: [p['score'] for p in predictions][k])
            predictions = [predictions[ix] for ix in order[::-1]]

    return render_template('coffee-classifier.html', img_src=img_src, predictions=predictions)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
