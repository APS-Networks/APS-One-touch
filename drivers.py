import os
import tarfile

import constants
from common import execute_cmd_n_get_output, get_env_var, dname, \
    create_symlinks, \
    is_ubuntu, get_switch_model, get_sde_profile_details
from constants import sde_module_bf_kdrv_string_value, \
     sde_module_bf_kpkt_string_value

installation_files = {
    "irq_debug_tgz": "./irq_debug.tgz"
}


def get_sde_modules():
    return get_sde_profile_details().get(constants.sde_modules_node)


def load_and_verify_kernel_modules():
    output = execute_cmd_n_get_output('lsmod')
    bf_mod = True
    i2c_i801 = True

    os.system("sudo modprobe -q i2c-i801")
    os.system("sudo modprobe -q i2c-dev")

    sde_module_names = get_sde_modules()
    if sde_module_names is not None:
        for module_name in sde_module_names:
            if module_name == sde_module_bf_kdrv_string_value:
                if module_name not in output:
                    load_bf_kdrv()
                else:
                    print('Module {} already loaded'.format(module_name))
            elif module_name == sde_module_bf_kpkt_string_value:
                if module_name not in output:
                    load_bf_kpkt()
                else:
                    print('Module {} already loaded'.format(module_name))
            else:
                print('Invalid module to load - {}.'.format(module_name))
                exit(0)
    else:
        print('Select at-least one SDE module to load in settings.xml')
        exit(0)

    output = execute_cmd_n_get_output('lsmod')

    if 'i2c_i801' not in output and is_ubuntu():
        # Ubuntu check is there because i2c_i801 appears only in output of
        # lsmod in Ubuntu
        i2c_i801 = False
        print('ERROR:i2c_i801 is not loaded.')

    if not any(mod in output for mod in [sde_module_bf_kdrv_string_value,
                                         sde_module_bf_kpkt_string_value]):
        bf_mod = False
        print("ERROR: Neither of {0}/{1} module loaded.".
              format(sde_module_bf_kdrv_string_value,
                     sde_module_bf_kpkt_string_value))

    # Load switch specific kernel modules
    if get_switch_model() == constants.bf2556x_1t:
        return bf_mod and i2c_i801 and load_and_verify_kernel_modules_bf2556()
    else:
        return bf_mod and i2c_i801 and load_and_verify_kernel_modules_bf6064()


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

    i2cbuses = execute_cmd_n_get_output('sudo -E i2cdetect -l')
    print(i2cbuses)
    if 'i2c-0' not in i2cbuses or\
            'i2c-1' not in i2cbuses or \
            'i2c-2' not in i2cbuses:
        print('Required I2C buses are not available in your device')
        exit(0)

    if 'irq_debug' not in output:
        install_irq_debug()

    # Verify that modules are loaded.
    output = execute_cmd_n_get_output('lsmod')

    if 'irq_debug' not in output:
        irq_debug = False
        print("ERROR:irq_debug is not loaded.")

    return irq_debug


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
    os.system("make clean")
    os.system("make")

    print("Installing module irq_debug.")
    os.system("sudo insmod ./irq_debug.ko")


def load_bf_kdrv():
    print("Loading bf_kdrv....")
    print("Using SDE {} for loading bf_kdrv.".format(get_env_var('SDE')))
    os.system(
        "sudo {0}/bin/bf_kdrv_mod_load {0}".format(
            get_env_var('SDE_INSTALL')))


def load_bf_kpkt():
    print("Loading bf_kpkt....")
    print("Using SDE {} for loading bf_kpkt.".format(get_env_var('SDE')))
    os.system(
        "sudo {0}/bin/bf_kpkt_mod_load {0}".format(
            get_env_var('SDE_INSTALL')))
