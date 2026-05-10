# models.py
from django.db import models
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL

class Password(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passwords')
    title = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='passwords/', null=True, blank=True)
    username = models.CharField(max_length=255, blank=True, null=True)  # Login/email
    url = models.URLField(blank=True, null=True)  # Sayt URL
    note = models.TextField(blank=True, null=True)  # Eslatma 
    views = models.IntegerField(default=0)
    
    # Shifrlangan parol
    encrypted_password = models.TextField(blank=True, null=True)
    
    # Har bir parol uchun unique salt
    encryption_salt = models.CharField(max_length=128, editable=False, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        unique_together = ['title', 'username']  # Bir xizmat uchun bitta parol
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def encrypt(self, master_password, plain_password):
        """
        Master password bilan parolni shifrlash
        """
        # Random salt yaratish
        salt = os.urandom(32)
        self.encryption_salt = base64.b64encode(salt).decode('utf-8')
        
        # Master passworddan shifrlash kalitini yaratish
        key = self._derive_key(master_password, salt)
        
        # Parolni shifrlash
        cipher = Fernet(key)
        self.encrypted_password = cipher.encrypt(plain_password.encode('utf-8')).decode('utf-8')
    
    def decrypt(self, master_password):
        """
        Master password bilan parolni deshifrlash
        """
        try:
            salt = base64.b64decode(self.encryption_salt)
            key = self._derive_key(master_password, salt)
            cipher = Fernet(key)
            decrypted = cipher.decrypt(self.encrypted_password.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError("Noto'g'ri master password yoki ma'lumot buzilgan")
    
    def _derive_key(self, master_password, salt):
        """
        Master passworddan shifrlash kalitini yaratish
        (Bu bir tomonlama emas, takrorlanuvchi)
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
    
    def update_password(self, old_master_password, new_master_password, new_plain_password=None):
        """
        Parolni yangilash (master password o'zgarganda)
        """
        try:
            # Eski parolni deshifrlash
            current_password = self.decrypt(old_master_password)
            
            # Agar yangi parol berilmagan bo'lsa, eskisini ishlat
            if new_plain_password is None:
                new_plain_password = current_password
            
            # Yangi master password bilan shifrlash
            self.encrypt(new_master_password, new_plain_password)
            self.save()
            return True
        except Exception as e:
            raise ValueError(f"Parolni yangilashda xatolik: {str(e)}")


class PasswordManager(models.Manager):
    def create_with_master_password(self, user, master_password, title, plain_password, **kwargs):
        """
        Master password bilan yangi parol yaratish
        """
        # Avval master passwordni tekshirish
        if not user.verify_master_password(master_password):
            raise ValidationError("Noto'g'ri master password")
        
        # Yangi parol yaratish
        password_entry = self.model(
            user=user,
            title=title,
            username=kwargs.get('username', ''),
            url=kwargs.get('url', ''),
            note=kwargs.get('note', ''),
            icon=kwargs.get('icon')
        )
        
        # Shifrlash
        password_entry.encrypt(master_password, plain_password)
        password_entry.save()
        
        return password_entry
    
    def get_decrypted(self, password_id, user, master_password):
        """
        Parolni deshifrlash
        """
        try:
            password_entry = self.get(id=password_id, user=user)
            decrypted_password = password_entry.decrypt(master_password)
            return password_entry, decrypted_password
        except Exception as e:
            raise ValidationError("Parolni ochishda xatolik")
    
    def get_all_decrypted(self, user, master_password):
        """
        Foydalanuvchining barcha parollarini deshifrlash
        """
        if not user.verify_master_password(master_password):
            raise ValidationError("Noto'g'ri master password")
        
        passwords = self.filter(user=user)
        result = []
        
        for pwd in passwords:
            try:
                decrypted = pwd.decrypt(master_password)
                result.append({
                    'id': pwd.id,
                    'title': pwd.title,
                    'username': pwd.username,
                    'password': decrypted,
                    'url': pwd.url,
                    'note': pwd.note,
                    'icon': pwd.icon,
                    'created_at': pwd.created_at,
                    'updated_at': pwd.updated_at
                })
            except:
                # Agar bir parol ochilmasa, uni o'tkazib yubor
                continue
        
        return result


class Messages(models.Model):
    for_all = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    published = models.BooleanField(default=True)
    viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} -- {self.published}"
    

        
class Category(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length = 300, null=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            unique_slug = slug
            count = 1
            qs = Category.objects.all()

            if self.id:
                qs = qs.exclude(id=self.id)

            while qs.filter(slug = unique_slug).exists():
                unique_slug = f"{slug}-{count}"
                count+=1
            self.slug = unique_slug

        return super().save(*args, **kwargs)
    

def format_number(value):
    if value >= 1000000000:
        return f"{value/1000000000:.2f}B"
    elif value >= 1_000_000:
        return f"{value/1000000:.2f}M"
    elif value >= 1_000:
        return f"{value/1000:.2f}k"
    return str(value)

class Article(models.Model):
    title = models.CharField(max_length=255)
    intro = models.TextField()
    cover = models.ImageField(upload_to='articles')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='article_author')
    read_time = models.DurationField(blank=True, null=True)
    views = models.ManyToManyField(User, related_name='article_views')
    published = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(unique=True, default="", null=True, blank=True)



    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:

            slug = slugify(self.title)
            unique_slug = slug
            count = 1
            qs = Article.objects.all()

            if self.id:
                qs = qs.exclude(id=self.id)

            while qs.filter(slug = unique_slug).exists():
                unique_slug = f"{slug}-{count}"
                count+=1
            self.slug = unique_slug
        return super().save(*args, **kwargs)
    
    @property
    def read_time_minute(self):
        return int(self.read_time.total_seconds() // 60)
    
    @property
    def str_views(self):
        count_views = self.views.count()
        return format_number(count_views)
    
    @property
    def comment_count(self):
        return self.comment_set.count()

class Content(models.Model):
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='contents/',null=True,blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return f"Content of {self.article.title}"



class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.author.username}: {self.text[:50]} ..."
    