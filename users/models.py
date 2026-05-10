from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
import hashlib
from django.utils import timezone

class User(AbstractUser):
    photo = models.ImageField(upload_to='users_photo/', null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    
    # Master passwordni tekshirish uchun (asl parol saqlanmaydi!)
    master_password_hash = models.CharField(max_length=128, null=True, blank=True)
    master_password_salt = models.CharField(max_length=64, null=True, blank=True)
    
    # Qachon master password o'rnatilgan
    master_password_set_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'auth_user'
    
    def set_master_password(self, master_password):
        """
        Master passwordni o'rnatish (faqat HASH saqlanadi)
        Bu method faqat BIRINCHI marta chaqiriladi
        """
        # Random salt yaratish
        salt = secrets.token_hex(32)
        self.master_password_salt = salt
        
        # PBKDF2 bilan hash yaratish
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            master_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iteratsiya
        )
        self.master_password_hash = hash_obj.hex()
        self.master_password_set_at = timezone.now()
        self.save()
    
    def verify_master_password(self, master_password):
        """
        Master passwordni tekshirish
        """
        if not self.master_password_hash:
            return False
        
        # Hashni tekshirish
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            master_password.encode('utf-8'),
            self.master_password_salt.encode('utf-8'),
            100000
        )
        
        # Time-attack hujumidan himoya
        return secrets.compare_digest(hash_obj.hex(), self.master_password_hash)
    
    def has_master_password(self):
        """Master password o'rnatilganligini tekshirish"""
        return bool(self.master_password_hash)
