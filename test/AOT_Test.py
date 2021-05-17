from __future__ import print_function

import sys
import unittest

import HtmlTestRunner

import bf_sde
import sal
from threading import Thread
import socket
import time
import os

from sal import get_sal_ip_port_dict


def is_port_up(host, port, retries=10, timeout=2):
    result = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(retries):
        result = sock.connect_ex((host, port))
        if result != 0:
            time.sleep(timeout)
        else:
            break
    sock.close()
    return not bool(result)


def kill_process(process_name):
    os.system("sudo killall -9 {}".format(process_name))


class AOTTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bf_sde.create_symlinks()
        bf_sde.build_sde()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_SAL_Build(self):
        self.assertTrue(sal.execute_user_action('c'))
        self.assertTrue(sal.execute_user_action('b'))
        self.assertTrue(sal.execute_user_action('c'))

    def test_SAL_Run(self):
        self.assertTrue(sal.execute_user_action('c'))
        self.assertTrue(sal.execute_user_action('b'))
        t = Thread(target=sal.execute_user_action, name='Run SAL', args=('r',))
        t.daemon = True
        t.start()
        time.sleep(5)
        for dev_ip, sal_grpc_port in get_sal_ip_port_dict().items():
            self.assertTrue(is_port_up(dev_ip, sal_grpc_port))
        self.assertTrue(sal.execute_user_action('c'))
        kill_process('salRefApp')

    def test_switchd_run(self):
        t = Thread(target=bf_sde.start_bf_switchd, name='bf_switchd')
        t.daemon = True
        t.start()
        self.assertTrue(
            is_port_up('127.0.0.1', 9999, retries=30, timeout=2))
        kill_process('bf_switchd')

    def test_build_bsp(self):
        self.assertTrue(bf_sde.install_switch_bsp())
        t = Thread(target=bf_sde.start_bf_switchd, name='bf_switchd')
        t.daemon = True
        t.start()
        self.assertTrue(
            is_port_up('127.0.0.1', 9999, retries=30, timeout=2))
        kill_process('bf_switchd')


if __name__ == '__main__':
    del sys.argv[1:]
    del sys.argv[2:]
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='report'))
