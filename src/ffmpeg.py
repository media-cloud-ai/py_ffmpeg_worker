
import os
import logging
import configparser
import subprocess

config = configparser.RawConfigParser()
config.read([
    'worker.cfg',
    '/etc/py_ffmpeg_worker/worker.cfg'
])

INPUT_PARAMS_MAPPING = {
    "input_codec_audio": "-codec:a",
    "input_codec_video": "-codec:v"
}

OUTPUT_PARAMS_MAPPING = {
    "audio_channels": "-ac",
    "audio_filters": "-af",
    "audio_sampling_rate": "-ar",
    "buffer_size": "-bufsize",
    "disable_audio": "-an",
    "disable_data": "-dn",
    "disable_video": "-vn",
    "force_overwrite": "-y",
    "max_bitrate": "-maxrate",
    "output_codec_audio": "-codec:a",
    "output_codec_video": "-codec:v",
    "pixel_format": "-pix_fmt",
    "profile_audio": "-profile:a",
    "profile_video": "-profile:v",
    "variable_bitrate": "-vbr",
    "video_filters": "-vf",
    "write_timecode": "-write_tmcd"
}

class FFmpeg():

    def __init__(self):
        self.load_configuration()

    def get_parameter(self, key, param):
        key = "FFMPEG_" + key
        if key in os.environ:
            return os.environ.get(key)

        return config.get('ffmpeg', param, fallback="")

    def load_configuration(self):
        self.ffmpeg_bin_path = self.get_parameter('BIN_PATH', 'bin_path')
        self.ffmpeg_lib_path = self.get_parameter('LIB_PATH', 'lib_path')
        self.ffmpeg_path = os.path.join(self.ffmpeg_bin_path, "ffmpeg")
        self.env = os.environ.copy()
        self.env["LD_LIBRARY_PATH"] = self.ffmpeg_lib_path


    def input_option_to_param(self, option_id):
        return INPUT_PARAMS_MAPPING.get(option_id, None)

    def is_input_option(self, option_id):
        return option_id in list(INPUT_PARAMS_MAPPING.keys())

    def input_options(self, options: list):
        result = []
        input_options = list(filter(lambda option: self.is_input_option(option["id"]), options))
        for option in input_options:
            key = self.input_option_to_param(option["id"])
            value = option["value"]
            if value is not False:
                result.append(key)
                if value is not True:
                    result.append(str(value))

        # Remove processed parameters
        remaining_options = list(filter(lambda option: not self.is_input_option(option["id"]), options))
        return (result, remaining_options)

    def output_option_to_param(self, option_id):
        param = OUTPUT_PARAMS_MAPPING.get(option_id, None)
        if param == None:
            param = "-" + option_id
        return param

    def output_options(self, options: list):
        result = []
        for option in options:
            key = self.output_option_to_param(option["id"])
            value = option["value"]
            if key != None and (value is not False):
                result.append(key)
                if value is not True:
                    result.append(str(value))
        return result

    def process(self, inputs: list, outputs: list, parameters: list):

        command = [self.ffmpeg_path]
        dst_paths = []

        for input_entry in inputs:
            (options, parameters) = self.input_options(parameters)
            command += options

            command.append("-i")
            if type(input_entry) is list:
                command = command + input_entry
            else:
                command.append(input_entry)

        for output in outputs:
            command += self.output_options(parameters)

            command.append(output)

            # Create missing output directory
            dst_dir = os.path.dirname(output)
            if not os.path.exists(dst_dir):
                logging.debug("Create output directory: %s", dst_dir)
                os.makedirs(dst_dir)

            dst_paths.append(output)

        print(command)
        # Process command
        logging.warn("Launching process command: %s", ' '.join(command))
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
