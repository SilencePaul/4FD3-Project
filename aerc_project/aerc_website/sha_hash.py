import base64
from Crypto.Hash import SHA3_256

class DataHasher:

    def __init__(self):
        self.encoding = "UTF-8"

    def hash(self, *plaintexts: str):
        sha = SHA3_256.new(''.join(plaintexts).encode(self.encoding))
        return base64.encodebytes(sha.digest()).decode(self.encoding)

    def verify(self, checksum: str, *plaintexts: str):
        return self.hash(*plaintexts) == checksum