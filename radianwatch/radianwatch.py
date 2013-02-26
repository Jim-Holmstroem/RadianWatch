from __future__ import print_function

from datetime import datetime
from sympy import *
import itertools as it
import functools as ft
import re
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE, STDOUT
import os
import BaseHTTPServer as httpserver

HOSTNAME, PORT = '192.168.1.85', 80

latex_template = "\\documentclass{{amsart}}\n\
\\usepackage{{color}} % For invisible frame\n\
\\usepackage{{amsmath}} % For invisible frame\n\
\\begin{{document}}\n\
    \\thispagestyle{{empty}} % No page numbers\n\
    {equation}\n\
\\end{{document}}\n".format 

prettier_radians = ft.partial( #\frac{x}{y}pi -> \frac{xpi}{y}
    re.sub,
    r"\\frac\{\s*(?P<m>[0-9]+)\s*\}\{\s*(?P<n>[0-9]+)\s*\}\s*\\pi",
    r"\\frac{\g<m>\pi}{\g<n>}"
)
remove_loneones = ft.partial( #removes 1\pi which just looks silly, could have forced it into prettier_radius but it whould get messy
    re.sub,
    r"\\frac\{1\\pi\}",
    r"\\frac{\pi}"
)

def png_render(filename):
    proc=Popen(
        [
            "latex2png", 
            "-g", 
            "-d", 
            "12800",
            str(filename)
        ],
        stdout=PIPE,
        stderr=PIPE,
        cwd='/tmp'
    )
    proc.wait()
    stdout, stderr = proc.communicate()
    print(stdout)
    get_png_filename = lambda filename: open(filename.replace('.tex','.png')) 
    #that is how latex2png works, didn't find workaround to specify the outputfile (another tempfile)
    png_file = get_png_filename(filename)
    png_data = png_file.read()
    png_file.close()
    os.remove(png_file.name)
    return "" #png_data

def latex2png(equation):
    with NamedTemporaryFile(suffix='.tex', delete=False) as f:
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
        f.file.write(latex_code)
        png_data = png_render(f.name)
    return png_data

time = datetime.time(datetime.now())

print(
    latex2png(
        equation=(
	    2*((3-time.hour)%24)*pi/12, #\in [0,4pi]
	    2*((15-time.minute)%60)*pi/60, #\in [0,2pi]
	    2*((15-time.second)%60)*pi/60 #\in [0,2pi]
        )#TODO change basis to be more radian like (start at x for example)
    )
)

class Handler(httpserver.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()



