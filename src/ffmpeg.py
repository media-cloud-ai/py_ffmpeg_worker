
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

        return config.get('ffmpeg', param, fallback="")

    def load_configuration(self):
        self.ffmpeg_bin_path = self.get_parameter('BIN_PATH', 'bin_path')
        self.ffmpeg_lib_path = self.get_parameter('LIB_PATH', 'lib_path')
        self.ffmpeg_path = os.path.join(self.ffmpeg_bin_path, "ffmpeg")
        self.env = os.environ.copy()
        self.env["LD_LIBRARY_PATH"] = self.ffmpeg_lib_path


    def input_option_to_param(self, option):
        if option == "input_codec_audio":
            return "-codec:a"
        if option == "input_codec_video":
            return "-codec:v"
        return None

    def input_options(self, options: list):
        result = []
        for option in options:
            key = self.input_option_to_param(option["id"])
            value = option["value"]
            if key != None and (value is not False):
                result.append(key)
                if value is not True:
                    result.append(str(value))
        return result

    def output_option_to_param(self, option):
        if option == "output_codec_audio":
            return "-codec:a"
        if option == "output_codec_video":
            return "-codec:v"
        if option == "force_overwrite":
            return "-y"
        if option == "disable_video":
            return "-vn"
        if option == "disable_audio":
            return "-an"
        if option == "disable_data":
            return "-dn"
        if option == "profile_audio":
            return "-profile:a"
        if option == "profile_video":
            return "-profile:v"
        if option == "audio_sampling_rate":
            return "-ar"
        if option == "audio_channels":
            return "-ac"
        if option == "variable_bitrate":
            return "-vbr"
        if option == "audio_filters":
            return "-af"
        if option == "video_filters":
            return "-vf"
        if option == "max_bitrate":
            return "-maxrate"
        if option == "buffer_size":
            return "-bufsize"
        if option == "preset":
            return "-preset"
        if option == "pixel_format":
            return "-pix_fmt"
        if option == "colorspace":
            return "-colorspace"
        if option == "color_trc":
            return "-color_trc"
        if option == "color_primaries":
            return "-color_primaries"
        if option == "rc_init_occupancy":
            return "-rc_init_occupancy"
        if option == "pixel_format":
            return "-pix_fmt"
        if option == "deblock":
            return "-deblock"
        if option == "write_timecode":
            return "-write_tmcd"
        if option == "x264-params":
            return "-x264-params"
        return None

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
            command += self.input_options(parameters)

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
