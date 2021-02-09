# APS One Touch (AOT)

AOT is an easy tool to setup APSN's switches. AOT configures BF2556X_1T and BF6064X_T with BF_SDE, BSP, SAL(Switch Abstraction Layer) and Stratum.
To get the files required by installer refer [Required Software](#required-software) section below.

Default input while execution i.e. when user just presses enter without any input appears in square braces i.e. '[n]' or '[do_nothing]'

## Required Software
|SW|Details|Where to get it|
|---|---|---|
|bf-reference-bsp-&lt;Release>-&lt;APSN switch model>_&lt;APSN ver>.zip|APSN Switches Platform package & Patch|APSN Support Portal|
|sal_&lt;Release>|Switch Abstraction Layer for APSN Switches|APSN Support Portal|
|bf-sde-&lt;Release>|Intel Tofino SDE|Intel's Support Portal|
|bf-reference-bsp-&lt;Release>|Intel Tofino SDE|Intel's Support Portal|
 
## Release Compatibility 
|Device|AOT|SAL|APSN BSP|SDE|OS (Recommended)|Kernel|
|---|---|---|---|---|---|---|
|BF6064X_T|v1.4.0|sal_1.1.1|bf-reference-bsp-9.3.0-BF6064_f536cae.zip|BF_SDE_9.3|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.3.0|sal_1.1.0|bf-reference-bsp-9.2.0-BF2556_5189449.zip<br>bf-reference-bsp-9.2.0-BF6064_0ee36ac.zip|BF_SDE_9.2|Ubuntu Server 18.04.4 LTS|4.15.x
|BF2556X_1T<br>BF6064X_T|v1.2.0|sal_1.1.0|BF2556X-1T_BSP_9.0.0(master HEAD)<br>BF6064X_BSP_9.0.0(master HEAD)|BF_SDE_9.1<br>BF_SDE_9.2|Ubuntu Server 18.04.4 LTS|4.15.x

## Quick start
For a quick start user should check for following node values in settings.yaml :
- SWITCH Model
- BF SDE
  - sde_pkg 
- BSP 
  - ref_bsp
  - aps_bsp_pkg 
- BUILD_PROFILES -> selected -> '*sde_hw_profile'

And do `python3 InstallAPS.py`
By default, all the package paths are calculated relative to user_home or relative to `PATH_PREFIX` if provided.

## settings.yaml
This is an input file for the AOT tool in order to minimize user inputs while installation.

By default, settings.yaml is picked up from project directory, But user can also give an absolute path to other custom setting file as a CLI argument while executing python scripts. 
This way user can save different settings in different files and need not to modify same file while launching AOT with different settings.
For Example - User may have 2 or more setting files based on SDE/BSP versions - settings_9.2.yaml and settings_9.3.yaml
And in order to build or run SDE 9.2 sal just do `python3 APS-One-touch/bf_sde.py ~/settings_9.2.yaml`
or to run SDE 9.3 do `python3 APS-One-touch/bf_sde.py ~/settings_9.3.yaml`
When used without any settings.yaml `python3 APS-One-touch/bf_sde.py` default settings.yaml from APS-One-touch directory is picked.

## advance_settings.yaml
advance_settings.yaml is useful for development usage only, e.g. For building SAL from the source.
For most of the users settings.yaml is enough to be configured and advance_settings.yaml can be ignored.

## How to run

- Install dependency packages :
  - `sudo apt install python3` (if not already installed)
  - `sudo apt install python` (python2.7 if not already installed, used by p4studio_build.py)
  - `sudo apt-get install libusb-1.0-0-dev` (required for BSP compilation)
  - `sudo apt-get install libcurl4-openssl-dev` (required for BSP compilation)
  - `sudo apt install i2c-tools`
  - `sudo apt install gcc-8 g++-8` (SAL is compiled using version 8 compiler)
- Start installation :
  - Direct trigger
    - To install and run SDE - `python3 bf_sde.py <optional - abs path to settings file>`
    - To run SAL - `python3 sal.py <optional - abs path to settings file>`
      and please note prerequisite to run SAL - SDE must be installed beforehand and 
      get SAL from APSN support unzip to APS-One-touch/release/sal dir 
      like: `unzip sal_<version>.zip -d APS-One-touch/release/sal`
    - To run stratum (prerequisite - SDE must be installed beforehand) - `python3 stratum.py <optional - abs path to settings file>`
  - Using AOT BUILD_PROFILES  
  Another method for installation is using `BUILD_PROFILES` in settings.yaml, 
    Building with a specific build profile takes care of prerequisite installation
    For example - if under `BUILD_PROFILES` the `selected` profile is `sal_hw_profile` and user executes `python3 InstallAPS.py` 
    this will trigger SDE installation automatically because SDE installation is a prerequisite for SAL to run, 
    prerequisites are mentioned under `deps` node for a particular profile. Actually this example scenario is equal to executing 
    `python3 bf_sde.py` and then `python3 sal.py`    

## Profiles

### sde_hw_profile
   Select the profile for installing BF_SDE and BSP on the switch. 
   Check 'BF SDE' and 'BSP' nodes configuration in settings.yaml.
   
### sal_hw_profile
   Select the profile for using Switch Abstraction Layer (SAL) on the switch.
   Get SAL release from APSN support portal, unzip it into APS-One-touch/release/sal directory. like: `unzip sal_<version>.zip -d APS-One-touch/release/sal`
   There is no other config to be done in settings.yaml by end user, SAL settings in advance_settings.yaml are for development usage.
   Check 'BF SDE', 'BSP' nodes configuration in settings.yaml.
   
### stratum_hw_profile
   For Stratum users on the switch.
   Check 'BF SDE', 'BSP', 'STRATUM' nodes configuration in settings.yaml.
   'SAL' integration with STRATUM is in progress so need not to configure 'SAL' for stratum_x_profile and  
   select 'do nothing' for SAL while executing stratum_x_profile. 
   
### x_sim_profile 
   Simulation profiles are used for development and experimentation only.

## Support
Raise issues in GitHub repo : <https://github.com/apsnw/APS-One-touch/issues> or in APSN support portal.
