#!/usr/bin/env python3

"""
@author: jimfan
"""
import dpts1
PDF_EXE = dpts1.__path__[0] +  '/bin/k2pdfopt-mac-2.35'


import os
import sys
import time
import logging
from collections import deque
from subprocess import Popen, PIPE

f_expand = os.path.expanduser


def trim_pdf(in_pdf, out_pdf, margin=0.15):
    # calls Willus' k2pdfopt to trim the whitespaces
    in_pdf = f_expand(in_pdf)
    old_out_pdf = f_expand(out_pdf)
    out_pdf = old_out_pdf[:-4] + '_temp.pdf'
    # tm: trim mode, x: exit on completion, om: output margin (inch)
    proc = Popen([PDF_EXE, in_pdf, '-mode', 'tm', '-x', '-o', out_pdf, '-om', '{0},{0},{0},{0}'.format(margin)], stdin=PIPE)
    proc.communicate(input=b'\n')
    os.system('mv -f "{}" "{}"'.format(out_pdf, old_out_pdf))


def trim_folder(folder='.', nested=0):
    for fname in os.listdir(folder):
        fname = os.path.join(folder, fname)
        if os.path.isdir(fname) and nested > 0:
            print('ENTERING SUBFOLDER', fname)
            trim_folder(fname, nested-1)
        if not fname.endswith('.pdf'):
            continue
        try:
            trim_pdf(fname, fname)
            print('successfully trimmed:', fname)
        except Exception as e:
            print('!'*30, fname, 'failed\n', e)


def main():
    folder = '.'
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    trim_folder(folder, nested=1)
