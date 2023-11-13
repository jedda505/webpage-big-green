import subprocess

subprocess.run('".venv/Scripts/activate.bat" & pip install Flask-Login', shell=True, text=True)

print("DONE")
