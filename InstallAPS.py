import os
import pprint
import tarfile
import zipfile

installation_files = {
    "bsp": "BF2556X-1T_BSP_9.0.0-master.zip",
    "sde": "bf-sde-9.0.0.tar",
    "irq_debug_tgz": "irq_debug.tgz",
    "mv_pipe_config_zip": "mv_pipe_config.zip"}

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

print(
    "All or subset of following packages can be installed. Default path for searching following installation files is {}, or give custom path during installation :".format(
        dname))
for key, val in installation_files.items():
    print("{}{}{}".format(key, " -> ", val))

######################################################################
######################################################################
sde_folder_path = ""
sde = installation_files["sde"]


# tar = tarfile.open(sde)
# sde_folder_path = os.getcwd() + "/" + tar.getnames()[0]
# tar.close()


def build_sde(sde_path):
    print("Building SDE from {}.".format(sde_path))
    if not tarfile.is_tarfile(sde_path):
        print("Invalid tofino SDE tar file {} can not build.".format(sde_path))
        return 0

    sde_tar = tarfile.open(sde_path)
    sde_folder_name = sde_tar.getnames()[0]
    global sde_folder_path
    sde_folder_path = sde_folder_name
    sde_tar.extractall()
    sde_tar.close()
    os.chdir(sde_folder_name)
    build_opt = "-up"
    default_profile = "p4_runtime_profile"
    profile_name = input(
        "Enter profile name to build SDE or i for interactive mode [{}]".format(
            default_profile))
    if not profile_name:
        profile_name = default_profile

    if profile_name == "i":
        build_opt = ""
        profile_name = ""

    sde_install_cmd = "./p4studio_build/p4studio_build.py {} {}".format(
        build_opt,
        profile_name)
    print(sde_install_cmd)
    os.system(sde_install_cmd)


def install_bf_sde():
    install_sde = input("Do you want to build SDE [y]/n?")
    if not install_sde:
        install_sde = "y"
    if install_sde == "y":
        sde_path = input("Enter the full path of sde tar [{}]?".format(sde))
        if not sde_path:
            sde_path = sde
        build_sde(sde_path)
    else:
        print("You selected not to build SDE.")


######################################################################
######################################################################
def checkBF_SDE_Installation():
    global sde_folder_path
    if not os.path.exists(sde_folder_path):
        sde_folder_path = input(
            "Enter full path of Barefoot SDE installation directory, was not found at [{}]:".format(
                "./"))
        if not os.path.exists(sde_folder_path):
            print(
                "Invalid Barefoot SDE installation directory {}, Exiting installer.".format(
                    sde_folder_path))
            exit(0)
    else:
        print(
            "Found BF SDE installation at {}, BSP will be installed in this SDE.".format(
                sde_folder_path))


def install_switch_bsp():
    install_bsp = input("Do you want to build BSP [y]/n?")
    if not install_bsp:
        install_bsp = "y"
    if install_bsp == "y":
        checkBF_SDE_Installation()
        os.chdir(dname)
        bsp_installation_file = input(
            "Enter full path of BSP installation package [{}]".format(
                installation_files["bsp"]))
        if not bsp_installation_file:
            bsp_installation_file = installation_files["bsp"]
        if zipfile.is_zipfile(bsp_installation_file):
            print("Installing {}".format(bsp_installation_file))
            zip_ref = zipfile.ZipFile(bsp_installation_file)
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
    print("Starting switchd without any P4 program, "
          "Useful to validate switch installation.")
    start_switchd = input(
        "Do you want to start switchd [y]/n?")
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
        irq = installation_files["irq_debug_tgz"]
        irq_file_path = input(
            "Enter path for irq_debug_driver [{}]".format(irq))
        if irq_file_path:
            irq = irq_file_path
        print("Installing irq debug drivers.")
        tar = tarfile.open(irq)
        irq_folder_name = tar.getnames()[0]
        tar.extractall()
        tar.close()
        print(irq_folder_name)
        os.chdir(irq_folder_name)
        os.system("make")
        print("Removing module irq_debug.")
        if os.system("sudo rmmod ./irq_debug.ko") != 0:
            print("Ignore above ERROR.")
        print("Installing module irq_debug.")
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
        mv_pipe_path = input(
            "Enter path for mv_pipe package [{}]".format(mv_pipe))
        if mv_pipe_path:
            mv_pipe = mv_pipe_path
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

def load_bf_kdrv():
    global sde_folder_path
    if not os.path.exists(sde_folder_path):
        sd_path = input("Enter path of BF SDE installation directory:")
        if os.path.exists(sd_path):
            sde_folder_path = sd_path
        else:
            print("Invalid path of BF SDE installation, Exiting installer.")
            exit(0)

    print("Using SDE {} for loading bf_kdrv.".format(sde_folder_path))
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_unload {}/install/".format(
            sde_folder_path, sde_folder_path))
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_load {}/install/".format(
            sde_folder_path, sde_folder_path))
    os.system("sudo modprobe -q i2c-dev")


######################################################################
######################################################################
if __name__ == '__main__':
    install_bf_sde()
    install_switch_bsp()
    install_irq_debug()
    install_mv_pipe()
    start_bf_switchd()
