#!/usr/bin/env python3
import runpy, os, sys, glob
here = os.path.dirname(__file__)
if here not in sys.path:
    sys.path.insert(0, here)
VENV = '/home/iqfrizqe/venv_dlfarm'
activate = os.path.join(VENV, 'bin', 'activate_this.py')
if os.path.exists(activate):
    with open(activate) as f:
        exec(f.read(), dict(__file__=activate))
else:
    for sp in glob.glob(os.path.join(VENV, 'lib', 'python*', 'site-packages')):
        if sp not in sys.path:
            sys.path.insert(0, sp)
ns = runpy.run_path(os.path.join(here, 'app.py'))
application = ns.get('application') or ns.get('app')
if application is None and 'create_app' in ns:
    application = ns['create_app']()
if application is None:
    raise RuntimeError("No WSGI application found in app.py. Ensure app.py defines 'app' or 'application' or 'create_app()'.")
