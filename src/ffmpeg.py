
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

        param_value = config.get('ffmpeg', param, fallback="")
        if param_value:
            return param_value
        raise RuntimeError("Missing '" + param + "' configuration value in 'ffmpeg' section.")

    def load_configuration(self):
        self.ffmpeg_bin_path = self.get_parameter('BIN_PATH', 'bin_path')
        self.ffmpeg_lib_path = self.get_parameter('LIB_PATH', 'lib_path')
        self.ffmpeg_path = os.path.join(self.ffmpeg_bin_path, "ffmpeg")
        self.env = os.environ.copy()
        self.env["LD_LIBRARY_PATH"] = self.ffmpeg_lib_path

    def process(self, inputs: list, outputs: list):

        command = [self.ffmpeg_path]
        dst_paths = []

        for input in inputs:
            options = input["options"]
            for key, value in options.items():
                command.append(key)
                if value is not True:
                    command.append(str(value))

            command.append("-i")
            command.append(input["path"])

        for output in outputs:
            options = output["options"]
            for key, value in options.items():
                command.append(key)
                if value is not True:
                    command.append(str(value))

            # Do not overwrite existing files if not specified
            if "-y" not in options:
                command.append("-n")

            path = output["path"]
            command.append(path)

            # Create missing output directory
            dst_dir = os.path.dirname(path)
            if not os.path.exists(dst_dir):
                logging.debug("Create output directory: %s", dst_dir)
                os.makedirs(dst_dir)

            dst_paths.append(path)

        # Process command
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

        return dst_paths

    def log_subprocess(self, stdout, stderr):
        if stdout:
            for line in stdout.decode("utf-8").split("\n"):
                logging.info("[FFmpeg Worker] " + line)
        if stderr:
            for line in stderr.decode("utf-8").split("\n"):
                logging.error("[FFmpeg Worker] " + line)
