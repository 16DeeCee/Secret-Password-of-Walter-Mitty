from cryptography.exceptions import InvalidKey,InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
import os

SALT_FIXED_LENGTH = 16 # 128-bit is recommended for Argon2
NONCE_FIXED_LENGTH = 12 # 96-bit is recommended for AES
MAX_HASH_KEY_LENGTH = 32 # 256-bit key is recommended

class Auth:
    def encrypt_password(plain_password: str) -> bytes:
        '''Encrypt password using AES Encryption.'''
        derived_key = Auth.generate_hash_key(plain_password, iterations=50)
        salt, key = derived_key[:SALT_FIXED_LENGTH], derived_key[SALT_FIXED_LENGTH:]
        aes_enc = AESGCM(key)
        nonce = os.urandom(NONCE_FIXED_LENGTH)
        encrypted_password = aes_enc.encrypt(nonce, plain_password.encode(), None)
        comb_bytes = salt + nonce + encrypted_password

        print(f"Salt: {salt} Salt length: {len(salt)}\nNonce: {nonce} Nonce length: {len(nonce)}\nEncrypted password: {encrypted_password} Encrypted password length: {len(encrypted_password)}")
        return comb_bytes
    
    
    def decrypt_password(plain_password: str, hidden_bytes: bytes) -> str:
        slice_index = NONCE_FIXED_LENGTH * 2
        salt = hidden_bytes[:SALT_FIXED_LENGTH]
        nonce =  hidden_bytes[NONCE_FIXED_LENGTH:slice_index]
        encrypted_pass = hidden_bytes[slice_index:]

        key = Auth.generate_hash_key(plain_password, salt, iterations=50)
        aes_dec = AESGCM(key[SALT_FIXED_LENGTH:])

        try:
            decrypted_pass = aes_dec.decrypt(nonce, encrypted_pass, None)
        except InvalidTag:
            raise ValueError("Master Password is incorrect.")

        return decrypted_pass.decode()
    

    def generate_hash_key(plain_password: str, salt: bytes = None, **kwargs) -> bytes:
        '''
        Hash password to generate key in AES encryption or for user authentication.
        
        pass this additional arguments (optional) to pass as a parameter for Argon2. \n
            length - pass\n
            iterations - pass\n
            lanes - pass\n
            memory_cost - pass\n
            ad - pass\n
            secret - pass
        '''
        if not salt:
            salt = os.urandom(SALT_FIXED_LENGTH)

        hash = Auth.argon_hash(salt, **kwargs)
        hashed_password = hash.derive(plain_password.encode("utf-8"))
        comb_bytes = salt + hashed_password
        
        return comb_bytes


    def verify_password(salt: str, plain_password: str, hashed_password: bytes) -> bool:
        hash = Auth.argon_hash(salt)

        try:
            hash.verify(plain_password.encode(), hashed_password)
        except InvalidKey:
            return False
    
        return True
    
    
    def argon_hash(
        salt: bytes, 
        iterations: int = 20, 
        lanes: int = 4, 
        memory_cost: int = 64 * 1024, 
        ad: bytes = None, 
        secret: bytes = None
    ) -> Argon2id:
        
        # print(salt, " ", length, " ", iterations, " ", lanes, " ", memory_cost, " ", ad, " ", secret)
        
        set_hash = Argon2id(
            salt=salt,
            length=MAX_HASH_KEY_LENGTH,
            iterations=iterations,
            lanes=lanes,
            memory_cost=memory_cost,
            ad=ad,
            secret=secret
        )

        return set_hash