import os
import tarfile
import zipfile

installation_files = {
    "bsp": "BF2556X-1T_BSP_9.0.0-master.zip",
    "sde": "bf-sde-9.0.0.tar",
    "set_sde_bash": "set_sde.bash",
    "irq_debug_tgz": "irq_debug.tgz",
    "mv_pipe_config_zip": "mv_pipe_config.zip"}

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

print("Checking if all required installation files are present...")
for key, val in installation_files.items():
    if not os.path.exists(val):
        print("{} is missing, Please contact Stordis Support.".format(val))
        exit(0)

print("Found all required files, Proceeding installation.")

######################################################################
######################################################################
sde_folder_path = ""
sde = installation_files["sde"]
tar = tarfile.open(sde)
sde_folder_path = os.getcwd() + "/" + tar.getnames()[0]
tar.close()


def build_sde(sde):
    print("Building SDE.")
    tar = tarfile.open(sde)
    sde_folder_name = tar.getnames()[0]
    tar.extractall()
    tar.close()
    os.chdir(sde_folder_name)
    sde_install_cmd = "./p4studio_build/p4studio_build.py -up p4_runtime_profile.yaml"
    print(sde_install_cmd)
    os.system(sde_install_cmd)


def install_bf_sde():
    install_sde = input("Do you want to build SDE [y]/n?")
    if not install_sde:
        install_sde = "y"
    if install_sde == "y":

        if tarfile.is_tarfile(sde):
            print("Extracting {}...".format(sde))
            build_sde(sde)
    else:
        print("You selected not to build SDE.")


######################################################################
######################################################################
def install_switch_bsp():
    os.chdir(dname)
    if not os.path.exists(sde_folder_path):
        print("Could not find {} exiting.".format(sde_folder_path))
        exit(0)

    install_bsp = input("Do you want to build BSP [y]/n?")
    if not install_bsp:
        install_bsp = "y"
    if install_bsp == "y":
        os.chdir(dname)
        bsp = installation_files["bsp"]
        if zipfile.is_zipfile(bsp):
            print("Installing {}".format(bsp))
            zip_ref = zipfile.ZipFile(bsp)
            zip_ref.extractall()
            extracted_dir_name = zip_ref.namelist()[0]
            zip_ref.close()
            os.chdir(extracted_dir_name)
            os.environ['BSP'] = os.getcwd()
            print("BSP home directory set to {}".format(os.environ['BSP']))
            os.environ['BSP_INSTALL'] = "{}/install".format(sde_folder_path)
            print(
                "BSP_INSTALL directory set to {}".format(
                    os.environ['BSP_INSTALL']))
            os.chdir("bf-platforms-9.0.0")
            os.system("autoreconf && autoconf")
            os.system("chmod +x ./autogen.sh")
            os.system("chmod +x ./configure")
            os.system(
                "./configure --prefix={} --enable-thrift --with-tof-brgup-plat".format(
                    os.environ['BSP_INSTALL']))
            os.system("make")
            os.system("sudo make install")
    else:
        print("You choose not to install BSP")


######################################################################
######################################################################
def start_bf_switchd():
    os.chdir(dname)
    start_switchd = input("Do you want to start switchd [y]/n?")
    if not start_switchd:
        start_switchd = "y"
    if start_switchd == "y":
        print("Starting switchd without p4 program")
        os.system(
            "sudo {0}/install/bin/bf_switchd --install-dir {0}/install "
            "--conf-file {0}/pkgsrc/p4-examples/tofino/tofino_skip_p4.conf.in "
            "--skip-p4".format(sde_folder_path))

######################################################################
######################################################################
def install_irq_debug():
    os.chdir(dname)
    install_irq_debug = input("Do you want to install irq_debug_drivers [y]/n?")
    if not install_irq_debug:
        install_irq_debug = "y"
    if install_irq_debug == "y":
        print("Installing irq debug drivers.")
        irq = installation_files["irq_debug_tgz"]
        tar = tarfile.open(irq)
        irq_folder_name = tar.getnames()[0]
        tar.extractall()
        tar.close()
        print(irq_folder_name)
        os.chdir(irq_folder_name)
        os.system("make")
        if os.system("sudo rmmod ./irq_debug.ko") != 0:
            print("Ignore above ERROR.")
        os.system("sudo insmod ./irq_debug.ko")
        os.system("sudo modprobe -q i2c-i801")


######################################################################
######################################################################
def install_mv_pipe():
    os.chdir(dname)
    build_mv_pipe_config = input("Do you want to build mv_pipe_config [y]/n?")
    if not build_mv_pipe_config:
        build_mv_pipe_config = "y"
    if build_mv_pipe_config == "y":
        mv_pipe = installation_files["mv_pipe_config_zip"]
        zip_ref = zipfile.ZipFile(mv_pipe)
        zip_ref.extractall()
        extracted_dir_name = zip_ref.namelist()[0]
        zip_ref.close()
        os.chdir(extracted_dir_name)
        os.system("gcc mv_pipe_config.c -o mv_pipe_config")
        os.system("sudo mkdir /delta")
        os.system("sudo cp ./mv_pipe_config /delta/")


######################################################################
######################################################################
if __name__ == '__main__':
    install_bf_sde()
    install_switch_bsp()
    install_irq_debug()
    install_mv_pipe()
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_unload {}/install/".format(
            sde_folder_path, sde_folder_path))
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_load {}/install/".format(
            sde_folder_path, sde_folder_path))
    os.system("sudo modprobe -q i2c-dev")
    start_bf_switchd()
