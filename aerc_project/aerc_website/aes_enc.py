import base64
from Crypto.Hash import BLAKE2b
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class DataCipher:

    def __init__(self, key: bytes, iv: bytes):
        self.encoding = "UTF-8"
        self.key = BLAKE2b.new(digest_bits=256).update(key).digest()  # 32 bytes
        self.iv = BLAKE2b.new(digest_bits=128).update(iv).digest()  # 16 bytes

    def encrypt(self, text: str):
        aes = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        cipher_data = aes.encrypt(pad(text.encode(self.encoding), AES.block_size))
        return base64.encodebytes(cipher_data).decode(self.encoding)

    def decrypt(self, b64: str):
        try:
            aes = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
            cipher_data = base64.decodebytes(b64.encode(self.encoding))
            plain_data = unpad(aes.decrypt(cipher_data), AES.block_size)
            return plain_data.decode(self.encoding)
        except:
            return b64