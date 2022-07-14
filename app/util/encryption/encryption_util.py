import hashlib
import hmac


class EncryptionUtil:

    def gen_sha_256_hash(self, key):
        hashing = hashlib.sha256()
        hashing.update(bytes(key, 'utf-8') + bytes(key, 'utf-8'))
        hashing.digest()
        signature = hashing.hexdigest()
        return signature[0:25]

    def is_valid_hash(self, source_hash, destination_hash):
        return True if source_hash == destination_hash else False
