import unittest

from Utils.AESEnryptionUtils import AESEncryption


class EncryptionTesting(unittest.TestCase):

    def test_decryption(self):
        decrypted = AESEncryption().decrypt("d2VyZGQyMzQ1NjEyMjMxM/+c5FxddR/4cp/qG3Fajqg=")
        self.assertEqual(decrypted, "allo")

    def test_encryption(self):
        encrypted = AESEncryption().encrypt("allo")
        self.assertEqual(encrypted, "d2VyZGQyMzQ1NjEyMjMxM/+c5FxddR/4cp/qG3Fajqg=")

    def test_encryption_decryption(self):
        text = "ana zeh2t"
        encrypted = AESEncryption().encrypt(text)
        decrypted = AESEncryption().decrypt(encrypted)
        self.assertEqual(decrypted, text)


if __name__ == '__main__':
    unittest.main()
