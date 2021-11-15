# APS One Touch (AOT)

AOT is an easy tool to setup APSN's switches. AOT configures BF2556X_1T and BF6064X_T with BF_SDE, BSP, SAL(Switch Abstraction Layer).
To get the files required by installer refer [Required Software](#required-software) section below.

While executing AOT, default input appears in square braces and will be picked up if user provides no input and just hits 'Enter',
e.g. '[n]' or '[do_nothing]'

## Required Software
Following SWs will be required to set up APSN switches, 
Please note - users can get all below SWs (except SDE) in a single archive with compatible releases from 'All in one package' section at APSN Support portal. 

|SW|Details|Where to get it|
|---|---|---|
|bf-reference-bsp-&lt;Release>-&lt;APSN switch model>_&lt;APSN ver>.zip|APSN BSP|APSN's Support Portal|
|sal_&lt;Release>|Switch Abstraction Layer for APSN Switches|APSN's Support Portal|
|bf-sde-&lt;Release>|Intel's Tofino SDE|Intel's Support Portal|
 
## Release Compatibility 
Following is the compatibility mapping among various SWs. Although those SWs can be downloaded from Intel's and APSN's support portals individually
but As mentioned above users can get all below SWs (except SDE and OS) in a single archive with compatible releases from 'All in one package' section at APSN Support portal.

|Device|AOT|SAL|APSN BSP|SDE|Ref-BSP|OS (Recommended)|Kernel|
|---|---|---|---|---|---|---|---|
|BF2556X_1T<br>BF6064X_T|v1.6.1|sal_1.3.5|bf-reference-bsp-9.7.0-BF2556_1.0.0.zip<br>bf-reference-bsp-9.7.0-BF6064_1.0.0.zip|BF_SDE_9.7.0|-|Ubuntu Server 20.04.x LTS|-
|BF2556X_1T<br>BF6064X_T|v1.5.3|sal_1.3.4|bf-reference-bsp-9.4.0-BF2556_1.0.4.zip<br>bf-reference-bsp-9.4.0-BF6064_1.0.1.zip|BF_SDE_9.5.0|bf-reference-bsp-9.5.0|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.5.2|sal_1.3.3|bf-reference-bsp-9.4.0-BF2556_1.0.3.zip<br>bf-reference-bsp-9.4.0-BF6064_1.0.1.zip|BF_SDE_9.5.0|bf-reference-bsp-9.5.0|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.5.1|sal_1.3.1|bf-reference-bsp-9.4.0-BF2556_1.0.2.zip<br>bf-reference-bsp-9.4.0-BF6064_1.0.1.zip|BF_SDE_9.4.0|bf-reference-bsp-9.4.0|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.5.0|sal_1.3.0|bf-reference-bsp-9.4.0-BF2556_1.0.2.zip<br>bf-reference-bsp-9.4.0-BF6064_1.0.1.zip|BF_SDE_9.4.0|bf-reference-bsp-9.4.0|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.4.2|sal_1.2.0|bf-reference-bsp-9.4.0-BF2556_1.0.1.zip<br>bf-reference-bsp-9.4.0-BF6064_1.0.1.zip|BF_SDE_9.4.0|bf-reference-bsp-9.4.0|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.4.1|sal_1.1.1|bf-reference-bsp-9.3.0-BF2556_1c5723d.zip<br>bf-reference-bsp-9.3.0-BF6064_f536cae.zip|BF_SDE_9.3.0|bf-reference-bsp-9.3.0|Ubuntu Server 18.04.4 LTS|5.4.x
|BF2556X_1T<br>BF6064X_T|v1.3.0|sal_1.1.0|bf-reference-bsp-9.2.0-BF2556_5189449.zip<br>bf-reference-bsp-9.2.0-BF6064_0ee36ac.zip|BF_SDE_9.2.0|bf-reference-bsp-9.2.0|Ubuntu Server 18.04.4 LTS|4.15.x
|BF2556X_1T<br>BF6064X_T|v1.2.0|sal_1.1.0|BF2556X-1T_BSP_9.0.0(master HEAD)<br>BF6064X_BSP_9.0.0(master HEAD)|BF_SDE_9.1<br>BF_SDE_9.2|NA|Ubuntu Server 18.04.4 LTS|4.15.x

## Quick start
For a quick start user should at least check for following node values in settings.yaml (No need to update settings.yaml if using 'All in one package' as it comes with preset configs according to its content) :
- BF SDE
  - sde_pkg 
- BSP 
  - aps_bsp_pkg 
-SAL
  - sal_home

By default, all the package paths are calculated relative to user_home or relative to `PATH_PREFIX` only if provided.

## settings.yaml
This is a configuration input file for the AOT tool, This file contains all the config parameters to install the APSN switches so that user has to provide minimal inputs during installation.

By default, settings.yaml is picked up from project directory i.e. APS-One-touch/settings.yaml,
But user can also provide path to custom settings file as a CLI argument while executing python scripts. 
This way user can save different settings in different files and need not to modify same file while launching AOT with different settings, 
User can quickly switch between different installations/configs just by changing CLI argument.
For Example - User may have 2 or more setting files with different config params based on SDE/BSP/SAL versions or config options e.g. ->
- settings_SDE_9.2.yaml for Installing/Building/Running SDE_9.2 version
- settings_SDE_9.3.yaml for Installing/Building/Running SDE_9.3 version
- settings_SDE_9.3_p4runtime.yaml for Installing/Building/Running SDE_9.3 with p4runtime profile.
- settings_SDE_9.3_switch_profile_sal_1.3.0.yaml for Installing/Building/Running SDE_9.3 with switch profile and SAL_1.3.0.

And then just use desired settings file as CLI arg to run SAL - `python3 APS-One-touch/sal.py ~/settings_9.2.yaml` or just to run SDE `python3 APS-One-touch/bf_sde.py ~/settings_SDE_9.3_p4runtime.yaml`

When used without any CLI arg e.g. - `python3 APS-One-touch/bf_sde.py` or `python3 APS-One-touch/sal.py` default APS-One-touch/settings.yaml is picked.

## advance_settings.yaml
advance_settings.yaml is useful for development usage only, e.g. For building SAL from the source.
For most of the end users settings.yaml is enough to be configured.

## How to run

- Install dependency packages :
  - `sudo apt install python3` (if not already installed)
  - `sudo apt install python` (python2.7 if not already installed, used by p4studio_build.py)
  - `sudo apt-get install libusb-1.0-0-dev` (required for BSP compilation)
  - `sudo apt-get install libcurl4-openssl-dev` (required for BSP compilation)
  - `sudo apt install i2c-tools`
  - `sudo apt install gcc-8 g++-8` (SAL is compiled using version 8 compiler)
- Start installation :
  - To install and run SDE - `python3 bf_sde.py <optional - abs path to custom settings.yaml>`
  - To run SAL - `python3 sal.py <optional - abs path to custom settings.yaml>`
    Please note - prerequisite to run SAL - SDE must be installed beforehand and 
    If not using 'All in one package' get SAL from APSN support and unzip to directory of choice, 
    like: `unzip sal_<version>.zip -d <dest_dir>` , Also check the path of <dest_dir> is same as configured in your settings file at SAL->sal_home,
    while running SAL AOT will pick sal executable as configured in settings file under SAL->sal_home. 

## Support
Raise issues in GitHub repo : <https://github.com/apsnw/APS-One-touch/issues> or in APSN's support portal.
s