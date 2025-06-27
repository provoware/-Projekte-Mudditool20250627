import subprocess, re

# Git-Tag auslesen
tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0']).decode().strip()
major, minor, patch = map(int, re.match(r'v?(\d+)\.(\d+)\.(\d+)', tag).groups())
new_patch = patch + 1
new_tag = f"v{major}.{minor}.{new_patch}"

# Tag setzen
subprocess.check_call(['git', 'tag', new_tag])
subprocess.check_call(['git', 'push', 'origin', new_tag])
# Version in __init__.py aktualisieren
def update_version_file(path, version):
    text = open(path).read()
    text = re.sub(r"__version__ = '[^']+'", f"__version__ = '{version}'", text)
    open(path, 'w').write(text)

update_version_file('Mudditool20250627/__init__.py', new_tag)
print(f'✅ Version auf {new_tag} gesetzt und gepusht.')
