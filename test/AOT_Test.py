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

import stratum


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
        self.assertTrue(is_port_up('127.0.0.1', 50054))
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

    @unittest.skip('')
    def test_build_stratum(self):
        self.assertTrue(stratum.execute_user_action('c'))
        self.assertTrue(stratum.execute_user_action('b'))

    @unittest.skip('')
    def test_run_stratum(self):
        self.assertTrue(stratum.execute_user_action('c'))
        self.assertTrue(stratum.execute_user_action('b'))
        t = Thread(target=stratum.execute_user_action, name='run_stratum',
                   args=('r',))
        t.daemon = True
        t.start()
        self.assertTrue(
            is_port_up('127.0.0.1', 28000, retries=30, timeout=2))
        self.assertTrue(
            is_port_up('127.0.0.1', 9999, retries=30, timeout=2))
        kill_process('stratum_bf')


if __name__ == '__main__':
    del sys.argv[1:]
    del sys.argv[2:]
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='report'))
