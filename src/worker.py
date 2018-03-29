#!/usr/bin/env python

import configparser
import json
import traceback
import logging
import os

from amqp_connection import Connection
from ffmpeg import FFmpeg

conn = Connection()

logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(message)s",
    level=logging.DEBUG,
)

config = configparser.RawConfigParser()
config.read([
    'worker.cfg',
    '/etc/py_ffmpeg_worker/worker.cfg'
])

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


def callback(ch, method, properties, body):
    try:
        msg = json.loads(body.decode('utf-8'))
        logging.debug(msg)

        try:
            parameters = msg['parameters']
            if 'requirements' in parameters:
                if not check_requirements(parameters['requirements']):
                    return False

            inputs = parameters["inputs"]
            outputs = parameters["outputs"]

            dst_paths = FFmpeg().process(inputs, outputs)

            logging.info("""End of process from %s to %s""",
                ', '.join(input["path"] for input in inputs),
                ', '.join(dst_paths))

            body_message = {
                "status": "completed",
                "job_id": msg['job_id'],
                "output": dst_paths
            }

            conn.sendJson('job_ffmpeg_completed', body_message)

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            error_content = {
                "body": body.decode('utf-8'),
                "error": str(e),
                "job_id": msg['job_id'],
                "type": "job_ffmpeg"
            }
            conn.sendJson('job_ffmpeg_error', error_content)

    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        error_content = {
            "body": body.decode('utf-8'),
            "error": str(e),
            "type": "job_ffmpeg"
        }
        conn.sendJson('job_ffmpeg_error', error_content)
    return True

conn.load_configuration(config['amqp'])

queues = [
    'job_ffmpeg',
    'job_ffmpeg_completed',
    'job_ffmpeg_error'
]

conn.connect(queues)
conn.consume('job_ffmpeg', callback)
