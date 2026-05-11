from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from main.models import Password
import re
from django_google_sso.models import GoogleSSOUser
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from .forms import CaptchaForm
from main.functions import send_email, generate_password
from random import randint
from django.conf import settings

# from django.contrib.auth.mixins import LoginRequiredMixin


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_username(username):
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return False
    if username.startswith('.') or username.endswith('.'):
        return False

    if '..' in username:
        return False

    if '__' in username:
        return False
    if username.isdigit():
        return False
    
    return True


class RegisterView(View):
    def get(self, request, context={}):
        recomended_pass = generate_password(
            length=randint(8,12), 
            lowercase='on',
            uppercase='on',
            number='on',
            punctuation='on'
            )
        context['recomended_pass'] = recomended_pass
        return render(request, "register.html", context)
    def post(self, request):
        data = request.POST
        password = data.get('password').strip() if data.get('password') else None
        password1 = data.get('password1').strip() if data.get('password1') else None
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        email = data.get('email').strip() if data.get('email') else None
        username = data.get('username').strip() if data.get('username') else None

        context = {
            'last_name': last_name,
            'first_name': first_name,
            'email': email,
            'username': username
        }

        error = False

        if not password:
            messages.error(request, "Parol kiritilishi shart!")
            error = True
        if not email:
            messages.error(request, "Email kiritilishi shart!")
            error = True
        if not username:
            messages.error(request, "Foydalanuvchi nomi kiritilishi shart!")
            error = True

        if password!=password1:
            messages.error(request, "Parol va Tasdiqlash paroli mos emas!")
            error = True
        elif len(password) < 8:
            messages.error(request, "Parol uzunligi kamida 8ta bo'lishi shart!")
            error = True
        elif len(set(password)) < (len(password) // 2 + 1):
            messages.error(request, "Kuchliroq parol tanlang!")
            error = True
        

        if not is_valid_email(email):
            messages.error(request, "Email noto'g'ri kiritildi!")
            error = True


        if not is_valid_username(username):
            messages.error(request, "Foydalanuvchi nomi katta va kichik harflar, raqamlar hamda _,. dan iborat bo'lishi kerak.")
            error = True
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bunday foydalanuvchi nomi band!")
            error = True

        if error:
            return self.get(request, context)
        
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        except Exception as ex:
            messages.error(request, "Ro'yhatdan o'tishda xatolik sodir bo'ldi, boshqa email kiritib sinab ko'ring.")
            print(ex)
            return self.get(request, context)

        messages.success(request, "Ro'yhatdan muvaffaqqiyatli o'tdingiz!")
        
        return redirect('login')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        captcha_form = CaptchaForm()
        context = {'captcha_form': captcha_form}
        return render(request, 'login.html', context)
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request):
        print(getattr(request, 'limited', 'No limit info'))
        data = request.POST

        password = data.get('password').strip() if data.get('password') else None
        username = data.get('username').strip() if data.get('username') else None

        error=False

        if not password:
            messages.error(request, "Parol kiritilishi shart!")
            error = True
        if not username:
            messages.error(request, "Foydalanuvchi nomi kiritilishi shart!")
            error = True

        if not is_valid_username(username):
            messages.error(request, "Foydalanuvchi nomi katta va kichik harflar, raqamlar hamda _,. dan iborat bo'lishi kerak.")
            error = True

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(request, "Bunday foydalanuvchi mavjud emas yoki foydalanuvchi nomi yoki parol noto'g'ri kiritildi!")
            error = True

        captcha_form = CaptchaForm(request.POST)
        if not captcha_form.is_valid():
            messages.error(request, "Captcha noto'g'ri kiritildi!")
            error = True
            
        if error:
            return redirect('login')
        
        login(request, user)
        messages.success(request, "Tizimga muvaffaqqiyatli kirdingiz!")
        return redirect('user-home')
        


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.error(request,"Tizimdan chiqdingiz!")
        return redirect('home')
        

class GoogleSSOCheck(View):
    def get(self, request):
        if request.user.is_authenticated:
            messages.success(request, "Tizimga muvaffaqqiyatli kirdingiz!")
            return redirect('user-home')
        messages.error(request, "Tanlangan emailda hisobingiz mavjud emas, iltimos kirish uchun avval ro'yhatdan o'ting!")
        return redirect('register')


        
def RateLimitView(request, exception=None):
    return render(request, 'rate-limit.html', status=429)



class MasterPasswordView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.has_master_password():
            messages.info(request, "Master Password allaqachon o'rnatilgan!")
            return redirect('user-home')
        context = {
            'header': "Master Password yaratish."
        }
        return render(request, "master_pass.html", context)
    
    def post(self, request):
        master_password = request.POST.get('master_password')
        if not master_password or master_password=='':
            messages.error(request, "Master password kiritilmagan!")
            return self.get(request)
        master_password = master_password.strip()
        if len(master_password)<8 or len(set(master_password))<5:
            messages.error(request, "Parol uzunligi kamida 8ta belgi bo'lishi va belgilar qaytarilishi 50 % dan kam bo'lishi shart!")
            return self.get(request)
        
        if settings.SMS_SERVICE_WORKING:
            request.session['mp_type'] = 'C'
            request.session['master_password'] = master_password
            request.session['mp_confirm_sended'] = False
            request.session['mp_confirm_try'] = 0
            return redirect('master-password-confirm')
        else:
            user = request.user
            user.set_master_password(master_password)
            messages.success(request, "Master Password o'rnatildi!")
            return redirect('user-home')

class MasterPasswordConfirmView(LoginRequiredMixin, View):
    def get(self, request):
        if 'master_password' not in request.session:
            return redirect('user-home')
        if request.session.get('mp_confirm_sended') is None:
            return redirect('user-home')
        if request.session.get('mp_confirm_sended') == False:
            confirm_code = str(randint(100000,999999))
            request.session['mp_confirm_code'] = confirm_code 
            send_email(request.user, confirm_code, "Master Paswordni saqlash")
            request.session['mp_confirm_sended'] = True
        mp_type = request.session['mp_type'] 
        context = {
            'header': f"Master Password ni {'saqlash' if mp_type=='C' else 'yangilash'} uchun emailingizga yuborilgan tasdiqlash parolini kiriting!",
            'input_name': 'confirm_code',
            'input_type': 'text'
        }
        print(request.session['mp_confirm_code'])  # o'chirilishi kerak
        return render(request, "master_pass.html", context)
    def post(self, request):
        confirm_code = request.POST.get('confirm_code')
        request.session['mp_confirm_try'] += 1
        if request.session['mp_confirm_code'] == confirm_code:
            user = request.user
            mp_type = request.session['mp_type']
            user.set_master_password(request.session['master_password'])
            user.save()
            if mp_type == "U":
                passwords = Password.objects.filter(user=user)
                for password in passwords:
                    try:
                        password.update_password(request.session['old_master_password'], request.session['master_password'])
                    except Exception as e:
                        print(e)
                request.session.pop('old_master_password', None)

            request.session.pop('mp_confirm_try', None)
            request.session.pop('mp_confirm_sended', None)
            request.session.pop('mp_confirm_code', None)
            request.session.pop('mp_type', None)
            request.session.set_expiry(3600)
            messages.success(request, f"Master password muvaffaqqiyatli {'o\'rnatildi' if mp_type=="C" else 'yangilandi'}!")
            return redirect('user-home')
        if request.session['mp_confirm_try'] >= 5:
            confirm_code = str(randint(100000,999999))
            request.session['mp_confirm_code'] = confirm_code 
            send_email(request.user, confirm_code, "Master Paswordni saqlash")
            request.session['mp_confirm_try'] = 0
            messages.info(request, "Tasdiqlash paroli qayta yuborildi, yangisini kiriting!")
        else:
            messages.error(request, "Tasdiqlash paroli noto'g'ri, qayta kiriting!")
        
        return redirect('master-password-confirm')


class EnterMasterPasswordView(LoginRequiredMixin, View):
    def get(self, request):
        if request.session.get('master_password'):
            messages.info(request, "Avvalroq master passwordni kiritgansiz!")
        context = {
            'header': "Master Password ni kiriting."
        }
        return render(request, "master_pass.html", context)
    def post(self, request):
        master_password = request.POST.get('master_password')
        if not master_password or master_password=='':
            messages.error(request, "Master password kiritilmagan!")
            return self.get(request)
        master_password = master_password.strip()
        user = request.user
        result = user.verify_master_password(master_password)
        if not result:
            messages.error(request, "Master password noto'g'ri kiritildi, qayta kiriting!")
            return self.get(request)
        request.session['master_password'] = master_password
        request.session.set_expiry(3600)
        messages.success(request, "Master Password tasdiqlandi!")
        return redirect('user-home')


class UpdateMasterPassword(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'header': "Master Passwordni yangilash."
        }
        return render(request, "update_master_pass.html", context)
    def post(self, request):
        master_password = request.POST.get('master_password')
        old_master_password = request.POST.get('old_master_password')

        if not old_master_password or old_master_password=='':
            messages.error(request, "Eski Master password kiritilmagan!")
            return self.get(request)

        if not request.user.verify_master_password(old_master_password):
            messages.error(request, "Joriy master password noto'g'ri kiritildi!")
            return self.get(request)
        
        if not master_password or master_password=='':
            messages.error(request, "Yangi Master password kiritilmagan!")
            return self.get(request)
        
        master_password = master_password.strip()
        if len(master_password)<8 or len(set(master_password))<5:
            messages.error(request, "Parol uzunligi kamida 8ta belgi bo'lishi va belgilar qaytarilishi 50 % dan kam bo'lishi shart!")
            return self.get(request)
        
        
        if settings.SMS_SERVICE_WORKING:
            request.session['mp_type'] = 'U'
            request.session['master_password'] = master_password
            request.session['old_master_password'] = old_master_password
            request.session['mp_confirm_sended'] = False
            request.session['mp_confirm_try'] = 0
            return redirect('master-password-confirm')
        else:
            user = request.user
            user.set_master_password(master_password)
            passwords = Password.objects.filter(user=user)
            for password in passwords:
                try:
                    password.update_password(old_master_password, master_password)
                except Exception as e:
                    print(e)
            messages.success(request, "Master Password yangilandi!")
            return redirect('user-home')
