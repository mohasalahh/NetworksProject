from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64


class AESEncryption:
    i = AES.block_size  # Constant 'i' representing the block size for AES

    def __init__(self):
        self.key = b'werdd23456122313'

    def encrypt(self, message):
        iv = self.key[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext_bytes = cipher.encrypt(self._pad(message.encode()))
        ciphertext = base64.b64encode(iv + ciphertext_bytes).decode('utf-8')
        return ciphertext

    def decrypt(self, ciphertext):
        ciphertext_bytes = base64.b64decode(ciphertext)
        iv = ciphertext_bytes[:self.i]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_bytes = cipher.decrypt(ciphertext_bytes[self.i:])
        decrypted_message = self._unpad(decrypted_bytes).decode('utf-8')
        return decrypted_message

    def _pad(self, message):
        padding_length = self.i - len(message) % self.i
        padding = bytes([padding_length]) * padding_length
        return message + padding

    def _unpad(self, message):
        padding_length = message[-1]
        return message[:-padding_length]
