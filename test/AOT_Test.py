from __future__ import print_function

import unittest

import HtmlTestRunner

import bf_sde
import sal
from threading import Thread
import socket
import time
import os

import stratum


class AOTTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_SAL_Build(self):
        self.assertTrue(sal.execute_user_action('c'))
        self.assertTrue(sal.execute_user_action('b'))
        self.assertTrue(sal.execute_user_action('c'))

    def isPortUp(self, host, port, retrires=10, timeout=2):
        result = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(retrires):
            result = sock.connect_ex((host, port))
            if result != 0:
                time.sleep(timeout)
            else:
                break
        sock.close()
        return not bool(result)

    def killProcess(self, processName):
        os.system("sudo killall -9 {}".format(processName));

    def test_SAL_Run(self):
        self.assertTrue(sal.execute_user_action('c'))
        self.assertTrue(sal.execute_user_action('b'))
        t = Thread(target=sal.execute_user_action, name='Run SAL', args=('r',))
        t.daemon = True
        t.start()
        self.assertTrue(self.isPortUp('127.0.0.1', 50052))
        self.assertTrue(sal.execute_user_action('c'))
        self.killProcess('salRefApp')

    @unittest.skip("This test runs long, Should run only in nightly build.")
    def test_SDE_build(self):
        self.assertTrue(bf_sde.create_symlinks())
        self.assertTrue(bf_sde.build_sde())

    def test_switchd_run(self):
        t = Thread(target=bf_sde.start_bf_switchd, name='bf_switchd')
        t.daemon = True
        t.start()
        self.assertTrue(
            self.isPortUp('127.0.0.1', 9999, retrires=30, timeout=2))
        self.killProcess('bf_switchd')

    def test_build_bsp(self):
        self.assertTrue(bf_sde.install_switch_bsp())
        t = Thread(target=bf_sde.start_bf_switchd, name='bf_switchd')
        t.daemon = True
        t.start()
        self.assertTrue(
            self.isPortUp('127.0.0.1', 9999, retrires=30, timeout=2))
        self.killProcess('bf_switchd')

    def test_build_stratum(self):
        self.assertTrue(stratum.execute_user_action('c'))
        self.assertTrue(stratum.execute_user_action('b'))

    def test_run_stratum(self):
        self.assertTrue(stratum.execute_user_action('c'))
        self.assertTrue(stratum.execute_user_action('b'))
        t = Thread(target=stratum.execute_user_action, name='run_stratum',
                   args=('r',))
        t.daemon = True
        t.start()
        self.assertTrue(
            self.isPortUp('127.0.0.1', 28000, retrires=30, timeout=2))
        self.assertTrue(
            self.isPortUp('127.0.0.1', 9999, retrires=30, timeout=2))
        self.killProcess('stratum_bf')


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='report'))
