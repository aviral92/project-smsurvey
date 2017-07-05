import unittest
import os
import inspect
import sys

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
pppp = os.path.dirname(ppp)
ppppp = os.path.dirname(pppp)
sys.path.insert(0, ppppp)

from smsurvey.core.security.secure import encrypt_password


class TestSecurity(unittest.TestCase):

    def test_encrypt_password_different_salts(self):
        one = encrypt_password("hello", os.urandom(16))
        two = encrypt_password("hello", os.urandom(16))
        self.assertNotEqual(one, two)

    def test_encrypt_password_same_salts(self):
        salt = os.urandom(16)
        one = encrypt_password("hello", salt)
        two = encrypt_password("hello", salt)
        self.assertEqual(one, two)

    def test_support_bytes(self):
        salt = os.urandom(16)
        one = encrypt_password("hello", salt)
        two = encrypt_password("hello".encode(), salt)
        self.assertEqual(one, two)
