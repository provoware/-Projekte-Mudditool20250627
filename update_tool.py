import subprocess, sys

def run(cmd):
    print(f"Running: {cmd}")
    if subprocess.call(cmd, shell=True) != 0:
        print(f"❌ Befehl fehlgeschlagen: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    run('flake8 .')   # Style-Checks
    run('mypy .')    # Typ-Checks
    run('pytest --maxfail=1 --disable-warnings -q')  # Tests
    run('bump2version patch')  # Version erhöhen
    print('✅ Alle Checks bestanden und Version erhöht.')
