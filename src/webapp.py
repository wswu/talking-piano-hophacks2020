import os
import subprocess
import time
import shutil

import cherrypy

import process_audio
import musescore_call
import visualize

class WebApp(object):
    @cherrypy.expose
    def index(self):
        with open("src/website/html5up-dimension/index.html") as f:
            return f.read()


    @cherrypy.expose
    def upload(self, fileToUpload, n_voices, keydiff_threshold, submit):
        dir_prefix = 'src/website/html5up-dimension/products/'

        with open("input.wav", "wb") as fout:
            fout.write(fileToUpload.file.read())

        print('processing audio')        
        process_audio.wav2midi("input.wav", dir_prefix+"output.mid",  {'n_peaks': int(n_voices), 'keydiff_threshold': int(keydiff_threshold)})

        print('generating pdf')
        musescore_call.generate_pdf(dir_prefix+"output.mid", dir_prefix+"output.pdf")
        
        print('generating mp3')
        musescore_call.generate_mp3(dir_prefix+"output.mid", dir_prefix+"output.mp3")

        print('generating video')
        visualize.visualize(dir_prefix+"output.mid", dir_prefix+"output.mp4")

        with open("src/website/html5up-dimension/pianotalks.html") as f:
            return f.read()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './src/website/html5up-dimension'
        }

        # [/style.css]
        # tools.staticfile.on = True
        # tools.staticfile.filename = "src/website/html5up-dimension/assets/css/main.css"

    }
    cherrypy.quickstart(WebApp(), '/', config=conf)
