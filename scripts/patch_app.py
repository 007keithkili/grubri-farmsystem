#!/usr/bin/env python3
"""
Safe patcher for app.py:
- makes a backup app.py.bak.TIMESTAMP
- inserts staff_list fetch after the first "conn = get_db_connection(); cur = conn.cursor()" (flexible whitespace)
- adds staff_members=staff_list to render_template('tasks.html', ...) if missing
- ensures "from flask import request, jsonify" is imported
- appends delete_task route before "if __name__ == '__main__':" or at file end
"""
import os, re, shutil, datetime, sys

ROOT = os.getcwd()
APP_PATH = os.path.join(ROOT, "app.py")

if not os.path.exists(APP_PATH):
    print("ERROR: app.py not found in", ROOT)
    sys.exit(2)

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
bak_path = APP_PATH + f".bak.{ts}"
shutil.copy2(APP_PATH, bak_path)
print("Backup created at", bak_path)

with open(APP_PATH, "r", encoding="utf-8") as f:
    text = f.read()

original = text

# 1) Ensure flask imports contain request and jsonify
# Try to find a "from flask import ..." line and add request,jsonify if missing.
m = re.search(r'^(from\s+flask\s+import\s+([^\n]+))', text, flags=re.MULTILINE)
if m:
    full_line = m.group(1)
    imports = m.group(2)
    # Normalize imports list (split by comma)
    names = [p.strip() for p in imports.split(",")]
    changed = False
    for needed in ("request", "jsonify"):
        if needed not in names:
            names.append(needed)
            changed = True
    if changed:
        new_line = "from flask import " + ", ".join(names)
        text = text.replace(full_line, new_line, 1)
        print("Updated Flask import line to include request, jsonify.")
else:
    # No 'from flask import' found; add one after the topmost import block (or at top)
    insert_at = 0
    # find end of initial shebang or docstring or first block of imports
    # naive: insert at top
    text = "from flask import request, jsonify\n" + text
    print("Inserted 'from flask import request, jsonify' at file top.")

# 2) Insert staff_list fetch after first occurrence of conn = get_db_connection(); cur = conn.cursor()
pattern = re.compile(r'conn\s*=\s*get_db_connection\(\)\s*;?\s*cur\s*=\s*conn\.cursor\(\)', re.IGNORECASE)
m = pattern.search(text)
if m:
    # determine line indentation for the matched line
    start = text.rfind('\n', 0, m.start()) + 1
    line_start = text[start:m.start()]
    indent_match = re.match(r'\s*', line_start)
    indent = indent_match.group(0) if indent_match else ''
    insert_block = (
        indent + "try:\n"
        + indent + "    cur.execute('SELECT id, first_name, last_name FROM staff ORDER BY first_name')\n"
        + indent + "    staff_list = cur.fetchall()\n"
        + indent + "except:\n"
        + indent + "    staff_list = []\n"
    )
    # place after the matched line (after m.end())
    insertion_point = m.end()
    text = text[:insertion_point] + "\n" + insert_block + text[insertion_point:]
    print("Inserted staff_list fetch into tasks() after cursor creation.")
else:
    print("Warning: cursor line not found. Please add staff_list fetch manually in tasks().")

# 3) Add staff_members argument to render_template('tasks.html', ...)
# Match return render_template('tasks.html' ... )
render_pattern = re.compile(r"return\s+render_template\(\s*(['\"]tasks\.html['\"])(?P<body>[^)]*)\)", re.DOTALL)
m2 = render_pattern.search(text)
if m2:
    body = m2.group("body")
    if "staff_members" in body:
        print("render_template already contains staff_members; no change.")
    else:
        # insert before closing ) but after existing args
        old = m2.group(0)
        new_body = body + ", staff_members=staff_list"
        new = "return render_template(" + m2.group(1) + new_body + ")"
        text = text.replace(old, new, 1)
        print("Added staff_members=staff_list to tasks() render_template call.")
else:
    print("Warning: Could not find render_template('tasks.html', ...). Add staff_members manually if needed.")

# 4) Append delete_task route (if not already present)
if "def delete_task(" in text:
    print("delete_task route already present; skipping append.")
else:
    delete_route = r"""

# --- API: delete task (AJAX) ---
@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task_old():
    try:
        # accept either form-encoded or JSON body
        task_id = request.form.get('task_id') or (request.get_json(silent=True) or {}).get('task_id')
        if not task_id:
            return jsonify({'success': False, 'message': 'Missing task_id'})
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute('DELETE FROM task WHERE id = ?', (task_id,))
        conn.commit(); conn.close()
        return jsonify({'success': True, 'message': 'Task deleted'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
"""
    # Insert before if __name__ == '__main__': if present
    main_pattern = re.search(r"\nif\s+__name__\s*==\s*['\"]__main__['\"]\s*:", text)
    if main_pattern:
        insert_at = main_pattern.start()
        text = text[:insert_at] + delete_route + "\n" + text[insert_at:]
        print("Appended delete_task route before main-run block.")
    else:
        text = text + "\n" + delete_route
        print("Appended delete_task route at file end.")

# 5) Save file (only if text changed)
if text != original:
    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched app.py written. Please inspect the file and run python -m py_compile app.py to check syntax.")
else:
    print("No changes made to app.py (it appears identical).")

print("Done. If you hit syntax errors after running, restore backup:", bak_path)
