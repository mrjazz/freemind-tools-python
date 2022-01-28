'''
Created on Nov 20, 2015

@author: denis
'''

import unittest
import tests.test_shell
import tests.test_freemind


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(tests.test_shell.ShellTestCase),
        unittest.TestLoader().loadTestsFromTestCase(tests.test_freemind.FreemindTestCase)
    ])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())