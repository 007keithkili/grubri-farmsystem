import runpy, traceback, os, sys
here = os.path.abspath('.')
try:
    ns = runpy.run_path(os.path.join(here,'app.py'))
    keys = [k for k in ns.keys() if k in ('app','application','create_app')]
    print("WSGI-related keys found:", keys)
    if 'create_app' in ns:
        try:
            a = ns['create_app']()
            print("create_app() returned:", type(a))
        except Exception:
            print("create_app() raised:")
            traceback.print_exc()
    elif 'app' in ns or 'application' in ns:
        print("WSGI object present.")
    else:
        print("No WSGI object found (app/application/create_app).")
except Exception:
    print("IMPORT TEST TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)
