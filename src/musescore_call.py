import subprocess

MUSESCORE_PATH = "C:/Program Files/MuseScore 3/bin/MuseScore3.exe"


def generate_pdf(input_mid, output_pdf):
    command = [MUSESCORE_PATH, "-M", "data/midi_import_options_0.xml",
               "-I", input_mid, "-o", output_pdf]
    subprocess.run(command)


def generate_mp3(input_mid, output_mp3):
    command = [MUSESCORE_PATH, "-M", "data/midi_import_options_0.xml",
               "-I", input_mid, "-o", output_mp3]
    subprocess.run(command)


def main():
    generate_pdf("yuzo.mid", "yuzo.pdf")
    generate_mp3("yuzo.mid", "yuzo.mp3")


if __name__ == "__main__":
    main()
