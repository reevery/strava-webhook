import logging
import json
from flask import abort
from google.cloud import secretmanager
from google.cloud import pubsub
import os

logger = logging.getLogger(__name__)


def index(request):
    logger.info('JSON: %s', request.get_json())
    logger.info('Args: %s', request.args)

    data = request.args

    if 'hub.mode' in data:
        # Get the Access Token
        client = secretmanager.SecretManagerServiceClient()
        resource_name = f"projects/{os.getenv('GCP_PROJECT')}/secrets/" \
                        f"STRAVA_VERIFY_TOKEN/versions/latest"
        verify_token = client.access_secret_version(resource_name)\
            .payload.data.decode('utf-8')

        if data['hub.mode'] != 'subscribe' \
                or data['hub.verify_token'] != verify_token:
            return 'Invalid request', 401

        # Valid request, return challenge
        return json.dumps({'hub.challenge': data['hub.challenge']}), 200

    data = request.get_json()

    if data['subscription_id'] != os.getenv('SUBSCRIPTION_ID'):
        logger.error('Invalid subscription ID')
        abort(400)
    if data['object_type'] == 'activity':
        publisher = pubsub.PublisherClient()
        publisher.publish(
            f"projects/{os.getenv('GCP_PROJECT')}/topics/strava-new-activity",
            json.dumps(data).encode('utf-8'))

        logger.info('Activity: %s', data['object_id'])
        return '', 200

    # Unhandled
    abort(400)
