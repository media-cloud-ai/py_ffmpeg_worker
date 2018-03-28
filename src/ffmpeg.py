
import os
import logging
import configparser
import subprocess

config = configparser.RawConfigParser()
config.read([
    'worker.cfg',
    '/etc/py_ffmpeg_worker/worker.cfg'
])

class FFmpeg():

    def __init__(self):
        self.load_configuration()

    def get_parameter(self, key, param):
        key = "FFMPEG_" + key
        if key in os.environ:
            return os.environ.get(key)

        return config.get('ffmpeg', param)

    def load_configuration(self):
        self.ffmpeg_bin_path = self.get_parameter('BIN_PATH', 'bin_path')
        self.ffmpeg_lib_path = self.get_parameter('LIB_PATH', 'lib_path')
        self.ffmpeg_path = os.path.join(self.ffmpeg_bin_path, "ffmpeg")
        self.env = os.environ.copy()
        self.env["LD_LIBRARY_PATH"] = self.ffmpeg_lib_path

    def process(self, inputs: list, options: dict, output: str):

        command = [self.ffmpeg_path]

        for path in inputs:
            command.append("-i")
            command.append(path)

        for key, value in options.items():
            command.append(key)
            if(value != True):
                command.append(str(value))

        dst_dir = os.path.dirname(output)
        if not os.path.exists(os.path.dirname(output)):
            logging.debug("Create output directory: %s", dst_dir)
            os.makedirs(dst_dir)

        command.append("-y")
        command.append(output)

        logging.debug("Launching process command: %s", ' '.join(command))
        ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.env)
        stdout, stderr = ffmpeg_process.communicate()
        self.log_subprocess(stdout, stderr)

        if stderr:
            message = "An error occurred processing "
            message += inputs + ": "
            message += stderr.decode("utf-8")
            raise RuntimeError(message)
        if ffmpeg_process.returncode != 0:
            message = "Process returned with error "
            message += "(code: " + str(ffmpeg_process.returncode) + "):\n"
            message += stdout.decode("utf-8")
            raise RuntimeError(message)

        return output

    def log_subprocess(self, stdout, stderr):
        if stdout:
            for line in stdout.decode("utf-8").split("\n"):
                logging.info("[FFmpeg Worker] " + line)
        if stderr:
            for line in stderr.decode("utf-8").split("\n"):
                logging.error("[FFmpeg Worker] " + line)
