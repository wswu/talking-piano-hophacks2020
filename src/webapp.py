import os
import subprocess

import cherrypy


class WebApp(object):
    @cherrypy.expose
    def index(self):
        with open("src/index.html") as f:
            return f.read()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.quickstart(WebApp(), config=conf)