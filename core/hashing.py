import hashlib
import os

def compute_hashes(file_path: str) -> dict:
    try:
        md5_hash = hashlib.md5()
        sha1_hash = hashlib.sha1()
        sha256_hash = hashlib.sha256()
        sha512_hash = hashlib.sha512()
        sha3_256_hash = hashlib.sha3_256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                sha256_hash.update(chunk)
                sha512_hash.update(chunk)
                sha3_256_hash.update(chunk)
                
        return {
            'md5': md5_hash.hexdigest(),
            'sha1': sha1_hash.hexdigest(),
            'sha256': sha256_hash.hexdigest(),
            'sha512': sha512_hash.hexdigest(),
            'sha3_256': sha3_256_hash.hexdigest(),
            'primary': sha256_hash.hexdigest(),
            'note': 'Hash values identify exact file content; a different modified file normally produces a different cryptographic hash.'
        }
    except Exception as e:
        return {'error': str(e)}
