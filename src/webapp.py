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
    def upload(self, fileToUpload, submit):
        print(fileToUpload.filename)

        with open("input.wav", "wb") as fout:
            fout.write(fileToUpload.file.read())

        process_audio.wav2midi("input.wav", "output.mid")
        musescore_call.generate_pdf("output.mid", "output.pdf")
        musescore_call.generate_mp3("output.mid", "output.mp3")
        visualize.visualize("output.mid", "output.mp4")
        
        return f"you uploaded {fileToUpload}"


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
