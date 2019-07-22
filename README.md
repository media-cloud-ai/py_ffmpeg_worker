# Python FFmpeg worker
Worker to run FFmpeg commands

Dependencies
------------

Depends on [py_amqp_connection](https://github.com/FTV-Subtil/py_amqp_connection) package:
```bash
pip3 install amqp_connection
```

Usage
-----

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
