from django.shortcuts import render, redirect
from .functions import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from .models import Password, Messages, Article, Content, Comment, Category
from users.models import User
from django.contrib import messages
from django.core.files import File
from django.db.utils import IntegrityError
from random import randint
from .functions import check_password, generate_password, get_feedback_from_ai
from django.urls import reverse
from hashlib import md5
from users.views import is_valid_email, is_valid_username
from django.db.models import Q

def main_view(request):
    context={}
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('user-home')
        uppercase=request.GET.get("uppercase","off")
        lowercase=request.GET.get("lowercase","off")
        number=request.GET.get("number","off")
        punctuation=request.GET.get("punctuation","off")
        length=request.GET.get("length","0")

        password=request.GET.get("password")
        result=request.GET.get("result")

        k=0
        for i in [uppercase,lowercase,number,punctuation]:
            if i=="on":
                k+=1
        if not 2<int(length)<33:
            context["exception"]="Parol uzunligi uchun 6 dan katta va 33 dan kichik qiymatlari kiritilishi kerak."
        elif k<2:
            context["exception"]="Parol generatsiyasi uchun kamida ikki xil belgi tanlashi kerak!"
        else:
            generated_password=generate_password(
                length=int(length),
                lowercase=lowercase,
                uppercase=uppercase,
                number=number,
                punctuation=punctuation
            )
            context["generated_password"]=generated_password

        count_passwords = Password.objects.all().count()
        count_users = User.objects.all().count()

        context['count_passwords'] = count_passwords
        context['count_users'] = count_users
        context["lowercase"]=lowercase
        context["uppercase"]=uppercase
        context["number"]=number
        context["punctuation"]=punctuation
        context["length"]=length

            
    elif request.method == "POST":
        password=request.POST.get("password")
        result=check_password(password)
        context["password"]=password
        context["result"]=result["feedback"]
        match result["feedback"]:
            case "Kuchsiz": color='red'
            case "Kuchsiz (Xavfli)": color='red'
            case "O'rtacha kuchlilik": color='#FFD966'
            case "Kuchli": color='teal'
            case "Juda kuchli": color='green'
        context["b_color"]=color

    return render(request,"index.html",context)

class UserHomeView(LoginRequiredMixin,View):
    def get(self, request): # Parollar ko'rinadigan sahifa
        passwords = Password.objects.filter(user=request.user).order_by('-views')
        for password in passwords:
            passwords.encrypted_password=None
            passwords.encryption_salt=None
        context={
            'passwords': passwords,
        }

        return render(request,'user-home.html', context)
    def post(self, request): # Parol qo'shish sorovi.
        if not request.session.get('master_password'):
            if not request.user.has_master_password():
                messages.error(request, "Hisobingiz uchun Master Password yaratmagansiz!")
                messages.error(request, "Avval, Parollarni saqlash uchun Master Password yaratishingiz shart!")
                messages.info(request, "Master Password parollarni bazada shifrlab saqlash uchun ishlatiladi!")
                return redirect('set-master-password')
            messages.error(request, "Parol saqlash uchun Master Passwordni kiritishingiz shart!")
            return redirect('enter-master-password')
        elif not request.user.verify_master_password(request.session.get('master_password')):
            messages.error(request, "Master Password noto'g'ri kiritilgan, qayta kiriting.")
            return redirect('enter-master-password')

        title = request.POST.get('title')
        username = request.POST.get('username')
        password = request.POST.get('password')
        icon = request.FILES.get('icon')
        url = request.POST.get('url')
        note = request.POST.get('note')

        if not all([title, username, password]):
            messages.error(request, "To'ldirilishi shart bo'lgan ustun to'ldirilmagan!")
            return redirect('user-home')
        try:
            password_obj = Password.objects.create(
                user = request.user,
                title = title,
                username = username
            )
        except IntegrityError:
            messages.error(request, f"Parol yaratish bekor qilindi, {title} uchun {username} avval yaratilgan!")
            return redirect('user-home')
        password_obj.encrypt(request.session.get('master_password'),password)
        if url:
            password_obj.url = url
        if note:
            password_obj.note = note
        if icon:
            if icon.size > 5*1024*1024:
                messages.warning(request, "Icon hajmi 5mb dan kattaligi sababli qabul qilinmadi!")
            elif icon.content_type not in ['image/jpeg', 'image/png', 'image/svg+xml']:
                messages.warning(request, "Icon fayl turi jpeg, png, svg dan biri bo'lishi shart, shu sababli qabul qilinmadi!")
            else:
                password_obj.icon = icon
        password_obj.save()
        messages.success(request, "Parol saqlandi!")
        return redirect('user-home')

                
    

    
class PasswordInfoView(LoginRequiredMixin,View):
    def get(self, request, id):
        try:
            password = Password.objects.get(id=id)
        except:
            messages.error(request, "Parol topilmadi!")
            return redirect('user-home')
        
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            if request.build_absolute_uri(reverse('user-home')) == previous_url:
                password.views += 1
                password.save()

        if request.GET.get('unhide') == 'on':
            if not request.session.get('master_password'):
                messages.error(request, "Avval Master Password ni kiriting!")
                return redirect('enter-master-password')
            else:
                if not request.user.verify_master_password(request.session.get('master_password')):
                    messages.error(request, "Master Passwordni kiriting!")
                    return redirect('enter-master-password')
            
            try:
                password.password = password.decrypt(request.session.get('master_password'))
            except Exception as e:
                messages.error(request, f"Xatolik:{e}")
                return redirect('password-info', id=id)
            unhide = 'on'
        else:
            password.encrypted_password=None
            password.encryption_salt=None
            password.password=randint(8,16)*'*'
            unhide = 'off'

        context = {
            'password': password,
            'unhide': unhide
        }

        if request.GET.get('unhide') == 'on':
            password_sessions = request.session.get('password_sessions', {})
            password_key = str(password.id)
            if password_key not in password_sessions:

                # AI + check faqat 1 marta ishlaydi
                check_result = check_password(password.password)
                ai_feedback = get_feedback_from_ai(check_result)

                check_result['rate']['repeat']['repeat_persentage'] = 100-check_result['rate']['repeat']['repeat_persentage']

                password_sessions[password_key] = {
                    'check_result': check_result,
                    'ai_feedback': ai_feedback
                }

                request.session['password_sessions'] = password_sessions
                request.session.set_expiry(3600)

            else:

                cached_data = password_sessions.get(password_key, {})

                check_result = cached_data.get('check_result')
                ai_feedback = cached_data.get('ai_feedback')

            
            context['check_result'] = check_result
            context['ai_feedback'] = ai_feedback

        return render(request, "password_info.html", context)
    
    def post(self, request, id):
        if not request.session.get('master_password'):
            messages.error(request, "Avval Master Password ni kiriting!")
            return redirect('enter-master-password')
        else:
            if not request.user.verify_master_password(request.session.get('master_password')):
                messages.error(request, "Master Password kiriting!")
                return redirect('enter-master-password')
        try:
            password = Password.objects.get(id=id)
        except:
            messages.error(request, "Bunday password topilmadi!")
            return redirect('user-home')
        if password.user != request.user:
            return redirect('user-home')
        
        if request.POST.get('post_type') == 'delete':
            password_sessions = request.session.get('password_sessions', {})
            if str(password.id) in password_sessions:
                password_sessions.pop(str(password.id), None)
            request.session['password_sessions'] = password_sessions
            request.session.set_expiry(3600)
            password.delete()

            messages.error(request, "Parol o'chirildi!")
            return redirect('user-home')
        elif request.POST.get('post_type') == 'edit':
            title = request.POST.get('title')
            username = request.POST.get('username')
            p = request.POST.get('password')
            icon = request.FILES.get('icon')
            url = request.POST.get('url')
            note = request.POST.get('note')

            if not all([title, username, password]):
                messages.error(request, "To'ldirilishi shart bo'lgan ustun to'ldirilmagan!")
                return redirect('user-home')
            
            password.title = title 
            password.username = username
            password.url = url if url else password.url
            password.note = note if note else password.note

            password.encrypt(request.session.get('master_password'),p)

            if icon:
                if icon.size > 5*1024*1024:
                    messages.warning(request, "Icon hajmi 5mb dan kattaligi sababli qabul qilinmadi!")
                elif icon.content_type not in ['image/jpeg', 'image/png', 'image/svg+xml']:
                    messages.warning(request, "Icon fayl turi jpeg, png, svg dan biri bo'lishi shart, shu sababli qabul qilinmadi!")
                else:
                    password.icon = icon
            password.save()
            messages.success(request, "Parol saqlandi!")
            return self.get(request, password.id)
        else:
            messages.warning(request, "Ko'zda tutilmagan post sorovi!")
            return redirect('user-home')
        

class PasswordGeneratorView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        uppercase=request.GET.get("uppercase","off")
        lowercase=request.GET.get("lowercase","off")
        number=request.GET.get("number","off")
        punctuation=request.GET.get("punctuation","off")
        length=request.GET.get("length","0")

        password=request.GET.get("password")
        result=request.GET.get("result")

        k=0
        for i in [uppercase,lowercase,number,punctuation]:
            if i=="on":
                k+=1
        if not 5<int(length)<33:
            context["exception"]="Parol uzunligi uchun 6 dan katta va 33 dan kichik qiymatlari kiritilishi kerak."
        elif k<2:
            context["exception"]="Parol generatsiyasi uchun kamida ikki xil belgi tanlashi kerak!"
        else:
            generated_password=generate_password(
                length=int(length),
                lowercase=lowercase,
                uppercase=uppercase,
                number=number,
                punctuation=punctuation
            )
            context["generated_password"]=generated_password

        context["lowercase"]=lowercase
        context["uppercase"]=uppercase
        context["number"]=number
        context["punctuation"]=punctuation
        context["length"]=length

        return render(request, 'user-password-generator.html', context)
    
def get_hash(password):
    h = md5(password.encode())
    return h.hexdigest()

class PasswordCheckerView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user-password-checker.html')
    def post(self, request):
        password = request.POST.get('password')
        if not password:
            return self.get(request)
        if len(password) < 1:
            return self.get(request)

        checked_pass = request.session.get('checked_pass', {})
        password_hash = get_hash(password)
        if password_hash in checked_pass:
            check_result = checked_pass[password_hash][0]
            ai_feedback = checked_pass[password_hash][1]
        else:
            check_result = check_password(password)
            check_result['rate']['repeat']['repeat_persentage'] = 100-check_result['rate']['repeat']['repeat_persentage']
            ai_feedback = get_feedback_from_ai(check_result)
            checked_pass[password_hash] = [check_result, ai_feedback]
            request.session['checked_pass'] = checked_pass
            request.session.set_expiry(3600)
        context = {
            'check_result': check_result,
            'ai_feedback': ai_feedback,
            'password': password
        }
        return render(request, 'user-password-checker.html', context)
    

class UserInfoViev(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "user-info.html")
    def post(self, request):
        user = request.user
        changed = False
        if request.POST.get('post_type') == 'edit':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            photo = request.FILES.get('photo')

            if first_name and len(first_name)>0 and first_name!=user.first_name:
                user.first_name = first_name
                changed = True
            if last_name and len(last_name)>0 and last_name!=user.last_name:
                user.last_name = last_name
                changed = True
            if username and len(username)>0 and username!=user.username:
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Bunday username band!")
                elif not is_valid_username(username):
                    messages.error(request, "Username noto'g'ri formatda kiritildi!")
                else:
                    user.username = username
                    changed = True
            if email and len(email)>0 and email!=user.email:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Bu email band!")
                elif not is_valid_email(email):
                    messages.error(request, "Email noto'g'ri formatda kiritildi!")
                else:
                    user.email = email
                    changed = True
            
            if photo:
                if photo.size > 5*1024*1024:
                    messages.warning(request, "Photo hajmi 5mb dan kattaligi sababli qabul qilinmadi!")
                elif photo.content_type not in ['image/jpeg', 'image/png', 'image/svg+xml']:
                    messages.warning(request, "Photo fayl turi jpeg, png, svg dan biri bo'lishi shart, shu sababli qabul qilinmadi!")
                else:
                    user.photo = photo
                    changed = True
            if changed:
                user.save()
                messages.info(request, "O'zgartirishlar saqlandi!")
            
        elif request.POST.get('post_type') == 'delete':
            confirm_text = request.POST.get('confirm_text')
            right_confirm_text = f"Mening {request.user.username} nomli hisobim o'chirilsin."
            confirm = request.POST.get('confirm')
            if confirm_text != right_confirm_text:
                messages.error(request, "Hisobni o'chirish matni noto'g'ri kiritildi!")
                return redirect('user-account')
            if confirm != 'on':
                messages.error(request, "Hisobni o'chirish uchun rozilik bildirilmagan!")
                return redirect('user-account')
            
            logout(request)
            user.delete()
            messages.warning(request, "Hisobingiz o'chirildi!")
            return redirect('home')
        
        elif request.POST.get('post_type') == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            if not old_password or len(old_password)<1:
                messages.error(request, "Joriy parol kiritilmagan!")
                return redirect('user-account')
            if not user.check_password(old_password):
                messages.error(request, "Joriy parol noto'g'ri kiritildi!")
                return redirect('user-account')
            if (not new_password) or (len(new_password) < 8) or (len(set(new_password)) < (len(new_password)//2+1)):
                messages.error(request, "Yangi parol uzunligi kamida 8ta bo'lishi hamda takrorlanganlik darajasi 50% dan kam bo'lishi shart!")
                return redirect('user-account')

            if old_password != new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Parolingiz o'zgartirildi!")

        else:
            messages.error(request, "Ko'zda tutilmagan post so'rovi!")
        return redirect('user-account')

class UserMessagesView(LoginRequiredMixin, View):
    def get(self, request):
        msgs = Messages.objects.filter(Q(for_all=True) | Q(user=request.user)).order_by('viewed', '-id')
        unread_count = msgs.filter(viewed=False).count()
        read_count = msgs.filter(viewed=True).count()

        context = {
            'msgs': msgs,
            'unread_count': unread_count,
            'read_count': read_count,
        }
        return render(request, 'user_message.html', context)
    
    def post(self, request):
        msg_id = request.POST.get('msg_id')
        try:
            msg_id = int(msg_id)
        except:
            messages.error(request, "Noto'g'ri sorov!")
            return self.get(request)
        try:
            msg = Messages.objects.filter(
                (Q(id = msg_id)) & (Q(user=request.user) | Q(for_all=True))
            ).first()
        except:
            messages.error(request, "Xabar topilmadi")
        else:
            if not msg:
                messages.error(request, "Xabar topilmadi!")
            else:
                if not msg.viewed:
                    msg.viewed = True
                    msg.save()
        return redirect('user-messages')
    


            

class ArticlesView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        have_articles = False
        category_filter = request.GET.get('category_filter')
        if not category_filter or category_filter == '__all__':
            articles = Article.objects.filter(published=True).order_by('-id')
        else:
            articles = Article.objects.filter(published=True, category__slug=category_filter).order_by('-id')
            context['selected_category_slug'] = category_filter
        if articles:
            categories = Category.objects.filter(article__in=articles).distinct()
            have_articles = True
            main_article = articles.order_by('-important', '-views', '-id').first()
            if not main_article:
                main_article = articles.first()
            other_articles = articles.exclude(id=main_article.id)
            context['categories'] = categories
            context['main_article'] = main_article
            context['other_articles'] = other_articles
        context['have_articles'] = have_articles

        return render(request, 'articles.html', context)

        

class ArticleContentView(LoginRequiredMixin, View):
    def get(self, request, slug):
        try:
            article = Article.objects.get(slug = slug)
        except:
            messages.error(request, "Maqola topilmadi!")
            return redirect('articles')
        if not article.views.filter(id=request.user.id).exists():
            article.views.add(request.user)
        
        contents = Content.objects.filter(article=article).order_by('id')
        comments = Comment.objects.filter(article=article)
        context = {
            'contents': contents, 
            'comments': comments,
            'article': article
        }
        return render(request, 'article-content.html', context)
    def post(self, request, slug):
        try:
            article = Article.objects.get(slug = slug)
        except:
            messages.error(request, "Maqola topilmadi!")
            return redirect('articles')
        text:str = request.POST.get('text')
        if not text or len(text)<1:
            messages.warning(request, "Izoh kamida 1 belgidan iborat bo'lishi kerak.")
            return redirect('article-content', slug=slug)
        text = text.strip()
        if len(text)<1:
            messages.warning(request, "Izoh kamida 1 belgidan iborat bo'lishi kerak.")
            return redirect('article-content', slug=slug)
        try:
            Comment.objects.create(
                author=request.user,
                text=text,
                article=article
            )
        except:
            messages.error(request, "Izoh obyekti yaratishda xatolik sodir bo'ldi!")
            return redirect('article-content', slug=slug)
        
        return redirect('article-content', slug=slug)