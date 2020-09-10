import os
import subprocess
import tarfile
import zipfile

import common
import constants
from common import execute_cmd_n_get_output, get_env_var, dname, \
    create_symlinks, \
    is_ubuntu, get_switch_model_from_settings

installation_files = {
    "irq_debug_tgz": "./irq_debug.tgz",
    "mv_pipe_config_zip": "./mv_pipe_config.zip"
}


def load_and_verify_kernel_modules():
    output = execute_cmd_n_get_output('lsmod')
    bf_kdrv = True
    i2c_i801 = True

    os.system("sudo modprobe -q i2c-i801")
    os.system("sudo modprobe -q i2c-dev")

    if 'bf_kdrv' not in output:
        load_bf_kdrv()

    output = execute_cmd_n_get_output('lsmod')

    if 'i2c_i801' not in output and is_ubuntu():
        # Ubuntu check is there because i2c_i801 appears only in output of lsmod in Ubuntu
        i2c_i801 = False
        print('ERROR:i2c_i801 is not loaded.')

    if 'bf_kdrv' not in output:
        bf_kdrv = False
        print("ERROR:bf_kdrv is not loaded.")

    # Load switch specific kernel modules
    if get_switch_model_from_settings() == constants.bf2556x_1t:
        return bf_kdrv and i2c_i801 and load_and_verify_kernel_modules_bf2556()
    else:
        return bf_kdrv and i2c_i801 and load_and_verify_kernel_modules_bf6064()


def load_and_verify_kernel_modules_bf6064():
    execute_cmd_n_get_output('sudo i2cset -y 0 0x70 0x20 \
    sudo i2cset -y 0 0x32 0xE 0x0 \
    sudo i2cset -y 0 0x32 0xF 0x0 \
    sudo i2cset -y 0 0x34 0x2 0x0 \
    sudo i2cset -y 0 0x34 0x3 0x0 \
    sudo i2cset -y 0 0x34 0x4 0x0 \
    sudo i2cset -y 0 0x35 0x2 0x0 \
    sudo i2cset -y 0 0x35 0x3 0x0 \
    sudo i2cset -y 0 0x35 0x4 0x0 \
    sudo i2cset -y 0 0x70 0x20 \
    sudo i2cset -y 0 0x32 0x14 0xff \
    sudo i2cset -y 0 0x32 0x15 0xff \
    sudo i2cset -y 0 0x34 0xB 0xff \
    sudo i2cset -y 0 0x34 0xC 0xff \
    sudo i2cset -y 0 0x34 0xD 0xff \
    sudo i2cset -y 0 0x35 0xB 0xff \
    sudo i2cset -y 0 0x35 0xC 0xff \
    sudo i2cset -y 0 0x35 0xD 0xff')
    return True


sde_folder_path = ""


def load_and_verify_kernel_modules_bf2556():
    output = execute_cmd_n_get_output('lsmod')
    irq_debug = True
    mv_pipe = True

    if 'irq_debug' not in output:
        install_irq_debug()

    if not os.path.exists("/delta/mv_pipe_config"):
        install_mv_pipe()

    # Verify that modules are loaded.
    output = execute_cmd_n_get_output('lsmod')

    if 'irq_debug' not in output:
        irq_debug = False
        print("ERROR:irq_debug is not loaded.")

    if not os.path.exists("/delta/mv_pipe_config"):
        mv_pipe = False
        print("ERROR:mv_pipe_config not installed.")

    return irq_debug and mv_pipe


def install_irq_debug():
    print("Installing irq_debug...")
    os.chdir(dname)
    print("Working dir :{}".format(dname))
    irq = installation_files["irq_debug_tgz"]
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
