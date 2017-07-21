import hashlib


def md5(data: str):
    m = hashlib.md5()
    m.update(data.encode())
    return m.hexdigest()
