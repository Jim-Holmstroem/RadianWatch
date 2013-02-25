from __future__ import print_function

from datetime import datetime
from sympy import *
import itertools as it

latex_template = "\\documentclass{{amsart}}\n\
\\usepackage{{color}} % For invisible frame\n\
\\usepackage{{amsmath}} % For invisible frame\n\
\\begin{{document}}\n\
    \\thispagestyle{{empty}} % No page numbers\n\
        {equation}\n\
\\end{{document}}\n".format 

print(latex_template(equation="t = \\left(\\frac{\\pi}{2},\\pi,\\frac{\\pi}{20} \\right)"))

time = datetime.time(datetime.now())

all_time = it.product(range(23),range(60))


for h, m in all_time:
    print(
        latex_template(
            equation=latex(
                (h*pi/12, m*pi/60) #TODO change basis to be more radian like (start at x for example)
            )
        )
    )

