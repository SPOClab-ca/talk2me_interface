import datetime
import hashlib
import os


# Create a persistent "pepper" for password hashing (same across all instances,
# but not stored in the database).
HASH_PEPPER = 'saltnpeppa'

def generate_confirmation_token(key):
    time_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    salt = os.urandom(16).encode('hex')
    h = hashlib.sha512()
    h.update(time_now + salt + key)
    return h.hexdigest()
