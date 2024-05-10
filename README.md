![NiceOptimizer Icon](.github_assets/icon.png)
# NiceOptimizer

My hobby Windows Optimizer project

# Installation

Go to releases, and download the compiled zip file (WILL BE AVALIBLE SOON)  
(make a exclusion for the tweaker because:  
1: I don't have a certificate  
2: There is a tweak what you can disable Windows Defender with, and windows defender detects it)

# Manual

Install python 3.8-3.10 with add to path enabled (IMPORTANT! NOT 3.12. IT WILL NOT WORK WITH 3.12.)  
Then, git clone this repo and cd into it in your new cmd window  
There type:  
`pip install -r requirements.txt`  
`python -m PyInstaller -Fw main.py --add-data "app;app" -i app\icon.ico --uac-admin`  
Go to dist, and there is your portable exe  
(NO SUPPORT FOR UPDATER YET!)

# License
MIT
