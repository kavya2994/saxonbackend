from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode



# aes = AESCipher("hello")
#
# aes.encrypt("klshfdoshohsdguioh")

# cipher = AES.new('hello i am an in'.encode('utf-8'), AES.MODE_CBC, 'This is an IV456'.encode('utf-8'))
# print(cipher.encrypt(b"hello"))


class Encryption:
    def __init__(self):
        # self.key = str(k).encode("utf-8")
        # self.iv = str(i).encode("utf-8")
        self.key = b'helloghdifjghcbv'
        self.iv = b'jdufhcndmvnchfue'

    def encrypt(self, data):
        data = data.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        # iv = b64encode(cipher.iv).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        # result = json.dumps({'iv':iv, 'ciphertext':ct})
        # print(iv)
        # print(ct)
        return ct

    def decrypt(self, data):
        ci = AES.new(self.key, AES.MODE_CBC, self.iv)
        dec = unpad(ci.decrypt(b64decode(data)), AES.block_size)
        # print(b64decode(data))
        return dec.decode("utf-8")

#
# print(Encryption().encrypt("admin"))
# print(Encryption().decrypt("y/sRjrTQ5uAA1vVmK4n6EQ=="))