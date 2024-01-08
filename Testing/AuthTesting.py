import unittest

from Client.RegistryThread import RegistryThread
from Peer.PeerThread import PeerThread


class AuthTest(unittest.TestCase):
    def setUp(self):
        self.registry = RegistryThread()
        self.registry.start()
        self.peer = PeerThread()
        self.peer.start()

    def test_login_failed(self):
        login_result = self.peer.login("hashed", "aaa", 16)
        self.assertNotEquals(login_result, 1)

    def test_creating_user(self):
        create_result = self.peer.create_account("test_user_11", "a")
        self.assertEqual(create_result, 1)

    def test_creating_user_exist(self):
        create_result = self.peer.create_account("test_user_11", "a")
        self.assertEqual(create_result, 0)

    def test_login_succeed(self):
        login_result = self.peer.login("test_user_11", "a", 13)
        self.assertEqual(login_result, 1)


if __name__ == '__main__':
    unittest.main()
