Set-ExecutionPolicy Unrestricted -Force -Scope CurrentUser
Invoke-Expression "& `"./Scripts/activate`""
pip install -r requirements.txt
Set-ExecutionPolicy Default -Force -Scope CurrentUser