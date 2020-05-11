import os
import subprocess
import tarfile
import zipfile

import common
from common import get_cmd_output, get_env_var, dname, create_symlinks, \
    is_ubuntu

installation_files = {
    #"bsp": "./BF2556X-1T_BSP_9.0.0-master.zip",
    #"sde": "./bf-sde-9.1.0.tar",
    "irq_debug_tgz": "./irq_debug.tgz",
    "mv_pipe_config_zip": "./mv_pipe_config.zip",
    #"stratum_repo": "https://github.com/stratum/stratum.git",
    #"sal": "./sal.zip",
    #"gb": "./gb.zip"
}

installation_dir = {
    "sde_home": "./bf-sde-9.1.0",
    "sal_home": "./sal",
    "gb_home": "./gb"
}

print(
    "All or subset of following packages can be installed. Default path for "
    "searching following installation files is {}, or give custom path during "
    "installation :".format(
        common.dname))
for key, val in installation_files.items():
    print("{}{}{}".format(key, " -> ", val))

sde_folder_path = ""
#sde = installation_files["sde"]
def load_and_verify_kernel_modules():
    output = get_cmd_output('lsmod')
    irq_debug = True
    bf_kdrv = True
    mv_pipe = True
    i2c_i801 = True

    os.system("sudo modprobe -q i2c-i801")
    os.system("sudo modprobe -q i2c-dev")

    if 'irq_debug' not in output:
        install_irq_debug()

    if 'bf_kdrv' not in output:
        load_bf_kdrv()

    if not os.path.exists("/delta/mv_pipe_config"):
        install_mv_pipe()

    loaded_modules = subprocess.run(['lsmod'], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    output = loaded_modules.stdout.decode('UTF-8')

    if 'i2c_i801' not in output and is_ubuntu():
        # Ubuntu check is there because i2c_i801 appears only in output of lsmod in Ubuntu
        i2c_i801 = False
        print('ERROR:i2c_i801 is not loaded.')

    if 'irq_debug' not in output:
        irq_debug = False
        print("ERROR:irq_debug is not loaded.")

    if 'bf_kdrv' not in output:
        irq_debug = False
        print("ERROR:bf_kdrv is not loaded.")

    if not os.path.exists("/delta/mv_pipe_config"):
        mv_pipe = False
        print("ERROR:mv_pipe_config not installed.")

    return irq_debug and bf_kdrv and mv_pipe and i2c_i801

def install_irq_debug():
    print("Installing irq_debug...")
    os.chdir(dname)
    print("Working dir :{}".format(dname))
    irq = installation_files["irq_debug_tgz"]
    # irq_file_path = input(
    #     "Enter path for irq_debug_driver [{}]".format(irq))
    # if irq_file_path:
    #     irq = irq_file_path
    print("Installing irq debug drivers.")
    create_symlinks()
    tar = tarfile.open(irq)
    irq_folder_name = tar.getnames()[0]
    tar.extractall()
    tar.close()
    print(irq_folder_name)
    os.chdir(irq_folder_name)
    os.system("make")

    print("Installing module irq_debug.")
    os.system("sudo insmod ./irq_debug.ko")

def install_mv_pipe():
    print("Building mv_pipe_config...")
    os.chdir(common.dname)
    mv_pipe = installation_files["mv_pipe_config_zip"]
    # mv_pipe_path = input(
    #     "Enter path for mv_pipe package [{}]".format(mv_pipe))
    # if mv_pipe_path:
    #     mv_pipe = mv_pipe_path
    zip_ref = zipfile.ZipFile(mv_pipe)
    zip_ref.extractall()
    extracted_dir_name = zip_ref.namelist()[0]
    zip_ref.close()
    os.chdir(extracted_dir_name)
    os.system("gcc mv_pipe_config.c -o mv_pipe_config")
    os.system("sudo mkdir /delta")
    os.system("sudo cp ./mv_pipe_config /delta/")

def load_bf_kdrv():
    print("Loading bf_kdrv....")
    print("Using SDE {} for loading bf_kdrv.".format(get_env_var('SDE')))
    os.system(
        "sudo {0}/bin/bf_kdrv_mod_load {0}".format(
            get_env_var('SDE_INSTALL')))
