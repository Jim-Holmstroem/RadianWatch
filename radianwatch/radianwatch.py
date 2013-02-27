from __future__ import print_function

from datetime import datetime
import time
from sympy import *
import itertools as it
import functools as ft
import re
from tempfile import NamedTemporaryFile
from subprocess import check_call, call, Popen, PIPE
import os
import BaseHTTPServer as httpserver

HOSTNAME, PORT = 'localhost', 80

latex_template = "\\documentclass{{minimal}}\n\
\\usepackage{{amsmath}} \n\
\\begin{{document}}\n\
    {equation}\n\
\\end{{document}}\n".format 

TMP_LOCATION="/tmp"
prettier_radians = ft.partial( #\frac{x}{y}\pi -> \frac{x\pi}{y}
    re.sub,
    r"\\frac\{\s*(?P<m>[0-9]+)\s*\}\{\s*(?P<n>[0-9]+)\s*\}\s*\\pi",
    r"\\frac{\g<m>\pi}{\g<n>}"
)
remove_loneones = ft.partial( #removes 1\pi which just looks silly, could have forced it into prettier_radius but it whould get messy
    re.sub,
    r"\\frac\{1\\pi\}",
    r"\\frac{\pi}"
)

def png_render(latex_code): #perhaps race conditions, shouldn't be any security issues as long as this file isn't writable
    proc=Popen(
        [
            "pdflatex", #doesn't really behave as a normal program, a little workarounding
            "-output-directory={tmp}".format(tmp=TMP_LOCATION),
            "--halt-on-error"
        ],
        shell=False,
        stdin=PIPE,
    )
    stdout, stderr = proc.communicate(latex_code) #also waits, only nice way to interagate with this ancient pdflatex, since it doesn't behave well.
    
    os.system(
        'pdfcrop {tmp}/texput.pdf {tmp}/texput-crop.pdf'.format(tmp=TMP_LOCATION)
    ) #pdfcrop doesn't work with Popen, gets: OSError: [Errno 8] Exec format error
    os.system(
        'convert -density 600 {tmp}/texput-crop.pdf {tmp}/texput.png'.format(tmp=TMP_LOCATION)
    ) #didn't work well with Popen :(

    png_file = open('{tmp}/texput.png'.format(tmp=TMP_LOCATION))
    png_data = png_file.read()
    png_file.close()
    return png_data

def latex2png(equation):
    latex_code = latex_template(
        equation=remove_loneones(
            prettier_radians(
                latex(
                    equation,
                    mode='inline'
                )
            )
        )
    )
    png_data = png_render(latex_code)
    return png_data

class Handler(httpserver.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(
            200
        )
        self.send_header(
            'Content-type', 
            'image/png'
        )
        self.send_header(
            'Content-disposition', 
            'filename=radianwatch.png'
        )
        self.end_headers()
        
        time = datetime.time(
            datetime.now()
        )
        png_data = latex2png(
            equation=(
                2*((3-time.hour)%24)*pi/12, #\in [0,4pi]
                2*((15-time.minute)%60)*pi/60, #\in [0,2pi]
                2*((15-time.second)%60)*pi/60 #\in [0,2pi]
            )
        )
        self.wfile.write(png_data)

if __name__ == "__main__":
    httpd = httpserver.HTTPServer(
        (HOSTNAME, PORT),
        Handler
    )
    print(
        time.asctime(), 
        "Server start - {name}:{port}".format(
            name=HOSTNAME, 
            port=PORT
        )
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(
        time.asctime(), 
        "Server stops - {name}:{port}".format(
            name=HOSTNAME, 
            port=PORT
        )
    )

