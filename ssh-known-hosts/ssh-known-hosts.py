from base64 import b64decode
import base64
import hmac

salt = b64decode("CuXixZ+EWfgz40wpkMugPHPalyk=")
host = b"192.168.0.2"
hash = hmac.HMAC(salt, host, 'sha1').digest()
print(base64.b64encode(hash).decode())
