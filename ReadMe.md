## APS One Touch ##

One touch is a tool to install all required software and tools for setting up Stordis's Advances Programmable Switches (APS) series.
Currently this tools configures BF2556X_1T with BF_SDE, BSP, SAL(Switch Abstraction Layer)
To get the files required by installer contact Stordis.

#### settings.yaml

This is an input file for the tool so as to minimize user inputs with frequent usage.
That should be the first file to be modified while starting preparing APS.
For quick start goto bottom of the file and type the profile of choice under selected. Also checks 'deps' and their 'details' for configuring path of SW packages, All package paths are calculated relative to user home untill PATH_PREFIX is empty.

#### How to run

- Installer uses python version 3 or later
  - sudo apt install python3
  - python3 InstallAPS.py
- Also, if dependencies for a specific SW module is already satisfied you can directly run the
 respective installation script for that module.
 e.g. You can directly trigger SAL installation as follows in case SDE (or BSP) already built and installed, This save user from giving inputs for dependency SWs installations.
 - python3 sal.py

#### Recommendations

- Ubuntu_18.05
- Recommended profiles - sal_hw_profile, sde_hw_profile

#### Upcoming Features

- Support for bf6064 switch, currently supports bf2556 switch only.
- Option for using pre-built binaries and Docker images.
- Building Stratum
