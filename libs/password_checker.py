import hashlib
import requests
from typing import Tuple
from libs.logging import Logging

log = Logging.getLogger()

class PasswordChecker:
    def hash_password(password: str) -> Tuple[str, str]:
        password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        password_head, password_tail = password_hash[:5], password_hash[5:]

        log.info("PASS HEAD: %s - PASS TAIL: %s" % (password_head, password_tail))

        return password_head, password_tail
    

    def leaked_password_api(hash_head: str) -> str:
        url = "https://api.pwnedpasswords.com/range/" + hash_head
        res = requests.get(url)

        if res.status_code != 200:
            raise RuntimeError(f"Error fetching data: {res.status_code}")
        
        return res.text


    def check_password(password: str) -> int:
        pass_head, hash_to_check = PasswordChecker.hash_password(password)
        leaked_hashes = PasswordChecker.leaked_password_api(pass_head)

        leaked_hashes = [hash.split(":") for hash in leaked_hashes.splitlines()]

        for hash in leaked_hashes:
            if hash[0] == hash_to_check:
                return hash[1]
            
        return 0