import platform
import os
import sys

project_dir = f'{os.path.sep}'.join(os.getcwd().split(os.path.sep)[:-1])
_os = backend = ''

if _os := platform.system():
    if _os == 'Linux':
        backend = os.path.join(project_dir, 'src', 'backend', 'linux', 'backend.py')
    elif _os == 'Windows':
        backend = os.path.join(project_dir, 'src', 'backend', 'windows', 'backend.py')

if ('os' in sys.argv) and ('backend' in sys.argv):
    print(_os, backend)
if 'os' in sys.argv:
    print(_os)
if 'backend' in sys.argv:
    print(backend)