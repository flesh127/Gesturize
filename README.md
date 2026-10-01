OS must be Windows

to install reqs:
pip install -r requirements.txt

to run:
Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd 'C:\Projects\Gesturize'; .\.venv\Scripts\Activate.ps1; python .\main.py"