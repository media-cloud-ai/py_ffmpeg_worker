#!/usr/bin/env python

import configparser
import json
import traceback
import logging
import os
import requests

from amqp_connection import Connection
from ffmpeg import FFmpeg

conn = Connection()

logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(message)s",
    level=logging.INFO,
)

config = configparser.RawConfigParser()
config.read([
    'worker.cfg',
    '/etc/py_ffmpeg_worker/worker.cfg'
])

# config['app']['verbosity']

ffmpeg = FFmpeg()

def check_requirements(requirements):
    meet_requirements = True
    if 'paths' in requirements:
        required_paths = requirements['paths']
        assert isinstance(required_paths, list)
        for path in required_paths:
            if not os.path.exists(path):
                logging.debug("Warning: Required file does not exists: %s", path)
                meet_requirements = False

    return meet_requirements

def get_config_parameter(config, key, param):
    if key in os.environ:
        return os.environ.get(key)

    if param in config:
        return config[param]
    raise RuntimeError("Missing '" + param + "' configuration value.")

def get_parameter(parameters, key, default):
    parameter = next((param for param in parameters if param['id'] == key), None)
    if parameter is None:
        return default

    value = None
    if 'default' in parameter:
        value = parameter['default']

    if 'value' in parameter:
        value = parameter['value']

    if parameter['type'] == 'credential':
        hostname = get_config_parameter(config['backend'], 'BACKEND_HOSTNAME', 'hostname')
        username = get_config_parameter(config['backend'], 'BACKEND_USERNAME', 'username')
        password = get_config_parameter(config['backend'], 'BACKEND_PASSWORD', 'password')

        response = requests.post(hostname + '/sessions', json={'session': {'email': username, 'password': password}})
        if response.status_code != 200:
            raise("unable to get token to retrieve credential value")

        body = response.json()
        if not 'access_token' in body:
            raise("missing access token in response to get credential value")

        headers = {'Authorization': body['access_token']}
        response = requests.get(hostname + '/credentials/' + value, headers=headers)

        if response.status_code != 200:
            raise("unable to access to credential named: " + key)

        body = response.json()
        value = body['data']['value']

    parameters.remove(parameter)
    return value


def callback(ch, method, properties, body):
    try:
        msg = json.loads(body.decode('utf-8'))
        logging.debug(msg)

        try:
            parameters = msg['parameters']
            requirements = get_parameter(parameters, 'requirements', {})
            if not check_requirements(requirements):
                return False

            input_paths = get_parameter(parameters, 'source_paths', None)
            output_paths = get_parameter(parameters, 'destination_paths', None)

            dst_paths = ffmpeg.process(input_paths, output_paths, parameters)

            logging.info("""End of process, generated %s""",
                ', '.join(dst_paths))

            body_message = {
                "status": "completed",
                "job_id": msg['job_id'],
                "output": dst_paths
            }

            conn.publish_json('job_ffmpeg_completed', body_message)

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            error_content = {
                "body": body.decode('utf-8'),
                "error": str(e),
                "job_id": msg['job_id'],
                "type": "job_ffmpeg"
            }
            conn.publish_json('job_ffmpeg_error', error_content)

    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        error_content = {
            "body": body.decode('utf-8'),
            "error": str(e),
            "type": "job_ffmpeg"
        }
        conn.publish_json('job_ffmpeg_error', error_content)
    return True


conn.run(config['amqp'],
        'job_ffmpeg',
        ['job_ffmpeg_completed',
         'job_ffmpeg_error'],
        callback
    )
