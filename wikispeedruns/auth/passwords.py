import bcrypt
import hashlib
import base64

from db import get_db


def valid_password(password: str) -> bool:
    if len(password) <= 7:
        return False

def hash_password(password: str) -> bytes:
    password = password.encode()
    return bcrypt.hashpw(base64.b64encode(hashlib.sha256(password).digest()), bcrypt.gensalt())

def check_password(user: dict, password: str) -> bool:
    ''' 
    For context, our original password hashing had an error, since it didn't account for NULL bytes
    in the sha256 hash by using base64 encoding (see bcrypt github)

    To remedy this, any old users (of which there were ~1000 when we discovered this) will have their
    password hash updated upon the first time they login. Therefore, we need to keep track of whether
    the user has the old hash (is_old_hash)
    '''
    id = user["user_id"]
    hash = user["hash"]

    if (user["is_old_hash"]):
        digest = hashlib.sha256(password.encode()).digest()

        # If there are NULL bytes, the password wouldn't have worked before
        # so it's definitely not right either
        if b'\0' in digest or not bcrypt.checkpw(digest, hash.encode()):
            return False

        # A user with a correct password, but old hash needs to have their password converted
        # to the new hash method
        new_hash = hash_password(password)

        db = get_db()
        with get_db().cursor() as cursor:
            cursor.execute("UPDATE users SET is_old_hash=0, hash=%s WHERE user_id=%s", (new_hash, id))
            db.commit()

        return True
    else:
        # If the password is updated, just use the check corr. with how we make the hashes
        return bcrypt.checkpw(base64.b64encode(hashlib.sha256(password.encode()).digest()), hash.encode())

