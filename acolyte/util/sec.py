import hashlib


def sha1(text):
    sh = hashlib.sha1(text.encode())
    return sh.hexdigest()
