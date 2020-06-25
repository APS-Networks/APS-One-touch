# APS One Touch

One touch is a tool to install all required software and tools for setting up STORDIS Advances Programmable Switches (APS) series.
This tools configures BF2556X_1T and BF6064X_T with BF_SDE, BSP, SAL(Switch Abstraction Layer) and Stratum
To get the files required by installer contact STORDIS.

## settings.yaml

This is an input file for the tool so as to minimize user inputs. settings.yaml should be the first file to be modified while preparing APS.
For quick start goto bottom of the file and type the profile of choice under selected. Also check 'deps' (dependencies profiles) and their 'details' for configuring path of SW packages, All package paths are calculated relative to user home until PATH_PREFIX is empty.
Configure correct path for selected and dependency profile packages.

## Profiles
   ### sde_hw_profile
   For the users who want to build BF_SDE and BSP on the switch. Check 'BF SDE' and 'BSP' nodes configuration in settings.yaml.
   ### sal_hw_profile
   For the users who want to develop their own applications for the switch, Switch Abstraction Layer (SAL).
   Check 'BF SDE', 'BSP', 'SAL' nodes configuration in settings.yaml.
   ### stratum_hw_profile
   For Stratum users on the switch.
   Check 'BF SDE', 'BSP', 'STRATUM' nodes configuration in settings.yaml. 'SAL' integration with STRATUM is in progress so need not to configure 'SAL' for stratum_x_profile and  
   select 'do nothing' for SAL while executing stratum_x_profile. 
   - x_sim_profile - Used for development.

## How to run

- Install dependency packages :
  - sudo apt install python3 (if not already installed)
  - sudo apt install python (python2.7 if not already installed, used by p4studio_build.py)
  - sudo apt-get install libusb-1.0-0-dev (required for BSP compilation)
  - apt-get install libcurl4-openssl-dev (required for BSP compilation)
- Start installation :
  - python3 InstallAPS.py
- Also, if dependencies for a specific profile are already installed you can directly run the
 respective installation script for that profile.
 e.g. You can directly trigger SAL installation by executing python3 sal.py, in case dependencies SDE and BSP are already installed, This save user from giving inputs for dependency SWs installations.

## Recommendations

- Ubuntu_Server_18.xx, Ubuntu_Server_16.xx
- Recommended profiles - sal_hw_profile, sde_hw_profile, stratum_hw_profile

## Upcoming Features

- Docker containerization.

## Support

Raise issues or provide suggestions by raising issues in GitHub repo : <https://github.com/stordis/APS-One-touch/issues>
