from __future__ import print_function

from datetime import datetime
from sympy import *
import itertools as it
import functools as ft
from subprocess import call
import re
from tempfile import NamedTemporaryFile

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

png_render = ft.partial(
    call,
    "latex2png",
    "-g",
    "-d 12800"
)

def latex2png(equation):
    with NamedTemporaryFile(suffix='.tex', delete=False) as f:
        latex_code = latex_template(
            equation=prettier_radians(
                latex(
                    equation,
                    mode='inline'
                )
            )
        )
        f.file.write(latex_code)
        png_render(f.name)
        print(f.name.replace('.tex','.png')) #that is how latex2png works
    return latex_code 

time = datetime.time(datetime.now())

print(
    latex2png(
        equation=(
            (
                2*((3-time.hour)%24)*pi/12, #\in [0,4pi]
                2*((15-time.minute)%60)*pi/60, #\in [0,2pi]
                2*((15-time.second)%60)*pi/60 #\in [0,2pi]
            ), #TODO change basis to be more radian like (start at x for example)
        )
    )
)

