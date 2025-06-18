from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import hashlib
from django.conf import settings
import bcrypt

class AESCipher:
    """
    AES加密解密工具类
    """
    def __init__(self, key=None):
        """
        初始化加密器
        """
        if key is None:
            key = settings.ENCRYPTION_KEY
            
        # 将密钥转为固定长度的SHA-256哈希
        self.key = hashlib.sha256(key.encode()).digest()
    
    def encrypt(self, plaintext):
        """
        加密明文
        """
        if not plaintext:
            return None
            
        # 生成随机IV
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # 加密并填充
        ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        
        # 组合IV和密文，并Base64编码
        return base64.b64encode(iv + ciphertext).decode('utf-8')
    
    def decrypt(self, encrypted_text):
        """
        解密密文
        """
        if not encrypted_text:
            return None
            
        try:
            # Base64解码
            encrypted_data = base64.b64decode(encrypted_text)
            
            # 分离IV和密文
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # 解密
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            return plaintext.decode('utf-8')
        except Exception:
            return None


def hash_password(password):
    """
    使用bcrypt哈希密码
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(password, hashed):
    """
    验证密码
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) 