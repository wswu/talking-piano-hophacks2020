# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 23:52:32 2020

@author: yuzoi
"""

import os
import main as mp
import configparser


configfile = 'options.cfg'
midifile = 'yuzo.mid'
config = configparser.ConfigParser()
config.read(configfile)
config.set("DEFAULT", "midi_filename", '../data/' + midifile )
with open(configfile, "w") as f:
    config.write(f)

mp.main(CONFIG=configfile)



