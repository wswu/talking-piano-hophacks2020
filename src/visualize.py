# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 23:52:32 2020

@author: yuzoi
"""

import os
import main as mp
import configparser


def visualize(input_midi, output_mp4):
    configfile = 'src/options.cfg'
    config = configparser.ConfigParser()
    config.read(configfile)
    config.set("DEFAULT", "midi_filename", input_midi)
    config.set("DEFAULT", "mp4_filename", output_mp4)
    with open(configfile, "w") as f:
        config.write(f)

    mp.main(CONFIG=configfile)


def main():
    visualize("output.mid", "output.mp4")


if __name__ == "__main__":
    main()
