
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

    def convert_options(self, options):
        result = []
        if isinstance(options, list):
            for option in options:
                key = option["id"]
                value = option["value"]
                if key == "input_codec_audio":
                    result.append("-codec:a")
                elif key == "output_codec_audio":
                    result.append("-codec:a")
                elif key == "input_codec_video":
                    result.append("-codec:v")
                elif key == "output_codec_video":
                    result.append("-codec:v")
                elif key == "force_overwrite":
                    result.append("-y")
                elif key == "disable_video":
                    result.append("-vn")
                elif key == "disable_audio":
                    result.append("-an")
                elif key == "disable_data":
                    result.append("-dn")
                elif key == "profile_audio":
                    result.append("-profile:a")
                elif key == "profile_video":
                    result.append("-profile:v")
                elif key == "audio_sampling_rate":
                    result.append("-ar")
                elif key == "audio_channels":
                    result.append("-ac")
                elif key == "variable_bitrate":
                    result.append("-vbr")
                elif key == "audio_filters":
                    result.append("-af")
                elif key == "max_bitrate":
                    result.append("-maxrate")
                elif key == "buffer_size":
                    result.append("-bufsize")
                elif key == "preset":
                    result.append("-preset")
                elif key == "pixel_format":
                    result.append("-pix_fmt")
                elif key == "colorspace":
                    result.append("-colorspace")
                elif key == "color_trc":
                    result.append("-color_trc")
                elif key == "color_primaries":
                    result.append("-color_primaries")
                elif key == "rc_init_occupancy":
                    result.append("-rc_init_occupancy")
                elif key == "pixel_format":
                    result.append("-pix_fmt")
                elif key == "deblock":
                    result.append("-deblock")
                elif key == "write_timecode":
                    result.append("-write_tmcd")
                elif key == "x264-params":
                    result.append("-x264-params")
                else:
                    result.append(key)

                if value is not True:
                    result.append(str(value))

        else:
            for key, value in options.items():
                if key == "input_codec_audio":
                    result.append("-codec:a")
                elif key == "output_codec_audio":
                    result.append("-codec:a")
                elif key == "input_codec_video":
                    result.append("-codec:v")
                elif key == "output_codec_video":
                    result.append("-codec:v")
                elif key == "force_overwrite":
                    result.append("-y")
                elif key == "disable_video":
                    result.append("-vn")
                elif key == "disable_audio":
                    result.append("-an")
                elif key == "disable_data":
                    result.append("-dn")
                elif key == "profile_audio":
                    result.append("-profile:a")
                elif key == "profile_video":
                    result.append("-profile:v")
                elif key == "audio_sampling_rate":
                    result.append("-ar")
                elif key == "audio_channels":
                    result.append("-ac")
                elif key == "variable_bitrate":
                    result.append("-vbr")
                elif key == "audio_filters":
                    result.append("-af")
                elif key == "max_bitrate":
                    result.append("-maxrate")
                elif key == "buffer_size":
                    result.append("-bufsize")
                elif key == "preset":
                    result.append("-preset")
                elif key == "pixel_format":
                    result.append("-pix_fmt")
                elif key == "colorspace":
                    result.append("-colorspace")
                elif key == "color_trc":
                    result.append("-color_trc")
                elif key == "color_primaries":
                    result.append("-color_primaries")
                elif key == "rc_init_occupancy":
                    result.append("-rc_init_occupancy")
                elif key == "pixel_format":
                    result.append("-pix_fmt")
                elif key == "deblock":
                    result.append("-deblock")
                elif key == "write_timecode":
                    result.append("-write_tmcd")
                elif key == "x264-params":
                    result.append("-x264-params")
                else:
                    result.append(key)

                if value is not True:
                    result.append(str(value))

        return result


    def process(self, inputs: list, outputs: list):

        command = [self.ffmpeg_path]
        dst_paths = []

        for input_entry in inputs:
            command += self.convert_options(input_entry["options"])

            command.append("-i")
            if type(input_entry["path"]) is list:
                command = command + input_entry["path"]
            else:
                command.append(input_entry["path"])

        for output in outputs:
            command += self.convert_options(output["options"])

            # Do not overwrite existing files if not specified
            #if "-y" not in options:
            #    command.append("-n")

            if "path" in output:
                path = output["path"]
                command.append(path)

                # Create missing output directory
                dst_dir = os.path.dirname(path)
                if not os.path.exists(dst_dir):
                    logging.debug("Create output directory: %s", dst_dir)
                    os.makedirs(dst_dir)

                dst_paths.append(path)

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
