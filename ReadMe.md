## APS One Touch ##
One touch is a tool to get and install all required software and tools required to set up Stordis Advances Programmable Switches (APS) series.
To get the files required by installer contact Stordis.
#### How to run
- Installer uses python version 3 or later
  - sudo apt install python3
- python3 InstallAPS.py 
#### Supported features
Installation of BF-SDE, Stordis BSP and all other required drivers on bf2556_1t switch running ONL/Ubuntu.
#### Upcoming Features
- Support for bf6064 switch, currently supports bf2556 switch only.
- Support for installing switch on ONL/ONLP and Ubuntu.
- Support for remote installation e.g. over ssh session.
- Get required installation artifacts via ftp (or so, using access provided by Stordis).
- Option for using pre-built binaries and Docker images of SDE and BSP.
- Pre-seeded OS images (Ubuntu and ONL/ONLP)