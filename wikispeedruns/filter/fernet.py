from cryptography.fernet import Fernet
import os

basedir = os.path.abspath(os.path.dirname(__file__))

def checkUsername(input):
        
    target = str(decrypt(load_key())).replace(" ", "")
    
    def func(e):
        return len(e)
    
    lol = target.split(",")
    lol.sort(key=func)
    
    for item in lol:
        if item in input:
            print(input, "FAILED")
            return False
    
    print(input)
    return True
    
def load_key():
    return open(os.path.join(basedir,'key.key'), "rb").read()

def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key
        
def encrypt(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open('filter.txt', "wb") as file:
        file.write(encrypted_data)

def decrypt(key):
    f = Fernet(key)
    with open(os.path.join(basedir,'filter.txt'), "rb") as file:
        encrypted_data = file.read()
    return f.decrypt(encrypted_data)

if __name__ == '__main__':
    #key = write_key()
    #encrypt('l.txt', key)
    print(checkUsername("thisshouldntcauseissues"))