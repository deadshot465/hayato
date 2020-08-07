Invoke-Expression "& `"./Scripts/activate`""
Set-ExecutionPolicy Unrestricted -Force -Scope CurrentUser
pip install -r requirements.txt
Set-ExecutionPolicy Default -Force -Scope CurrentUser