import unittest
import figgypy.config

import sys
import os

class TestConfig(unittest.TestCase):
    def test_config_load(self):
        os.environ['FIGGY_GPG_HOME']='test-keys'
        c = figgypy.config.Config('test-config.json')
        self.assertEquals(c.db, 'db.heck.ya')
        self.assertEquals(c.secrets['hush_hush'], 'i-u-i')


if __name__ == '__main__':
    unittest.main()
