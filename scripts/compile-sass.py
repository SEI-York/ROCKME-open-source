'''
Use libsass to compile the project's sass files
'''
import sys
import os

import sass


BASE = os.getcwd()  # .rpartition('/')[0]
PROJECT = sys.argv[1]
STATIC = '{}/{}/static'.format(BASE, PROJECT)

sass.compile(
    dirname=(
        '{}/sass'.format(STATIC),
        '{}/css'.format(STATIC)
    ),
    output_style='expanded'
)
