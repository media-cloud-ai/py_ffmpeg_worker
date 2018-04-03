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
  "job_id": "1",
  "parameters": {
    "requirements": {
      "paths": [
        "/path/to/required/file"
      ]
    },
    "inputs": [
      {
        "path": "/path/to/source/file",
        "options": {
          ...
        }
      },
      ...
    ],
    "outputs": [
      {
        "path": "/path/to/destination/file",
        "options": {
          "-codec:a": "pcm_s24le",
          "-vn": true,
          ...
          "-ar": 48000
        }
      },
      ...
    ]
  }
}
```

See [FFmpeg website](https://www.ffmpeg.org/) for more options & usage details.
