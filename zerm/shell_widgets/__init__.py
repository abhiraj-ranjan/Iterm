from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
for f in modules:
    if (not isfile(f)) or f.endswith('__.py') or (not f.endswith('.py')):
        modules.remove(f)
        
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

