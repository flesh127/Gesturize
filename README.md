OS must be Windows

to install reqs:
pip install -r requirements.txt

to run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd '<path to project folder>'; .\.venv\Scripts\Activate.ps1; python .\main.py"