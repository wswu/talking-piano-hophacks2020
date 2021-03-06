import configparser
import os

import visualize_midi as mp
import ffmpeg


def visualize(input_midi, output_mp4):
    configfile = 'src/options.cfg'
    config = configparser.ConfigParser()
    config.read(configfile)
    config.set("DEFAULT", "midi_filename", input_midi)
    config.set("DEFAULT", "mp4_filename", output_mp4)

    if os.path.exists(output_mp4):
        os.remove(output_mp4)

    with open(configfile, "w") as f:
        config.write(f)

    mp.main(CONFIG=configfile)
    input_video = ffmpeg.input(output_mp4)
    input_audio = ffmpeg.input(input_midi)
    # ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_mp4).run()


def main():
    visualize("output.mid", "output.mp4")


if __name__ == "__main__":
    main()
