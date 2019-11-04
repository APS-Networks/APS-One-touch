import os
import tarfile
import zipfile

bsp = "BF2556X-1T_BSP_8.9.0-master.zip"
sde = "bf-sde-8.9.0.tar"
set_sde_bash = "set_sde.bash"

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

##Check for presense of required files###
if not os.path.exists(bsp) or not os.path.exists(sde) or not os.path.exists(
        set_sde_bash):
    print("One or more of the required files are missing.")
    exit(0)

if tarfile.is_tarfile(sde):
    print("Extracting {}...".format(sde))
    tar = tarfile.open(sde)
    sde_folder_name = tar.getnames()[0]
    if os.path.exists(sde_folder_name):
        i = input("SDE seems to be installed already, do you want to install sde again[y]/n?")
        if i == "y":
            tar.extractall()
            tar.close()
            os.chdir(sde_folder_name)
            os.system("source ..{}".format(set_sde_bash))
            sde_install_cmd = "./p4studio_build/p4studio_build.py -up p4_runtime_profile"
            os.system(sde_install_cmd)


os.chdir(dname)

if zipfile.is_zipfile(bsp):
    print("Installing {}".format(bsp))
    zip=zipfile.ZipFile(bsp)
    os.chdir(zip.namelist()[0])
    os.system("export BSP=`pwd`")
    os.system("export BSP_INSTALL=$SDE_INSTALL")
    os.chdir("bf-platforms-8.9.0")
    os.system("chmod +x ./install_pltfm_deps.sh")
    os.system("./install_pltfm_deps.sh")
    os.system("autoreconf")
    os.system("autoconf")
    os.system("./configure --prefix=$BSP_INSTALL --enable-thrift")
    os.system("make")
    os.system("sudo make install")

os.system("sudo modprobe -q i2c-dev")
os.system("sudo modprobe -q i2c-i801")
