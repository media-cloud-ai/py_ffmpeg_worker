# Python FFmpeg worker

Worker to run FFmpeg commands


## Requirements

Depends on [py_amqp_connection](https://github.com/FTV-Subtil/py_amqp_connection) package:
```bash
pip3 install amqp_connection
```

## Usage

Example of handled AMQP message body:

```json
{
  "job_id": 1,
  "parameters": [
    {
      "id": "requirements",
      "type": "requirements",
      "value": {
        "paths": [
          "/path/to/video_file.avi",
          "/path/to/audio_file.wav"
        ]
      }
    },
    {
      "id": "source_paths",
      "type": "array_of_strings",
      "value": [
        "/path/to/video_file.avi",
        "/path/to/audio_file.wav"
      ]
    },
    {
      "id": "output_codec_video",
      "type": "string",
      "value": "copy"
    },
    {
      "id": "output_codec_audio",
      "type": "string",
      "value": "copy"
    },
    {
      "id": "map",
      "type": "string",
      "value": "0:0"
    },
    {
      "id": "map",
      "type": "string",
      "value": "1:0"
    },
    {
      "id": "force_overwrite",
      "type": "boolean",
      "value": true
    },
    {
      "id": "destination_paths",
      "type": "array_of_strings",
      "value": [
        "/path/to/destination_file.mp4"
      ]
    }
  ]
}
```

See [FFmpeg website](https://www.ffmpeg.org/) for more options & usage details.

## CI / CD

A `.gitlab-ci.yml` file is provided for the gitlab CI/CD feature.
This file will instantiate te following pipeline:

<!-- language: lang-none -->
    /----------\
    |  Docker  |
    \----------/
         |
     +-------+
     | build |
     +-------+
            

### Docker

The command `make docker-build` will build an image named `mediacloudai/ffmpeg_worker`.

The command `make push-docker-registry` will logged in and push the built image in the official docker registry. The login must be set with the following environment variables:

| Variable name           | Default value              | Description                                      |
|-------------------------|----------------------------|--------------------------------------------------|
| `DOCKER_REGISTRY_LOGIN` |                            | User name used to connect to the docker registry |
| `DOCKER_REGISTRY_PWD`   |                            | Password used to connect to the docker registry  |

