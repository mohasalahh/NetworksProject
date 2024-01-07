from Utils import AESEnryptionUtils

encrypted = AESEnryptionUtils.AESEncryption().encrypt("allo")
decrypted = AESEnryptionUtils.AESEncryption().decrypt(encrypted)

print(encrypted)
print(decrypted)