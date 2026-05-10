SecurePass - Parollarni xavfsiz saqlash platformasi.
Tuzuvchi haqida:
    Yo'nalish: Axborot Xavfsizligi
    Guruh: 641-23
    FIO: Ro'zimatov Shuhratjon Isoqjon o'g'li
    Telegram: @shuhratrozimatov (https://t.me/shuhratrozimatov)
    E-pochta: shuhratrozimatov06@gmail.com

Tizim arxitekturasi:
Backend: Python, Django
Frontend: HTML, CSS, JavaScript

Tizimni ishga tushirish:
1. Zipdan ochilgan virtual muhitni ishga tushirish uchun ushbu fayl manzilida terminal oching va quyidagi buyruqni yozing:
   python -m venv env
2. Virtual muhitni aktivatsiya qiling:
   env/Scripts/Activate.ps1
3. Talab qilinadigan kutubxonalarni o'rnatish:
   pip install -r requirements.txt
4. Loyihani ishga tushirish:
   python manage.py runserver

Loyihada yana Redis ham qo'llanilgan, ishga tushirish uchun Redisni yuklab oling. Redis yuklangan fayl manzilida terminal ochib quyidagi buyruqni yozing:
(avvalgi ochilgan terminalni yopib qo'ymang!)
   .\redis-server.exe --port 6380

Loyihada gmaildan xabar yuborish va Ai feedback xususiyatlari ham mavjud, ularni ishlashi uchun .env fayliga quyidagi qiymatlarni kiriting:
   GOOGLE_SSO_CLIENT_ID=
   GOOGLE_SSO_PROJECT_ID=
   GOOGLE_SSO_CLIENT_SECRET=
   SMTP_DOMAIN=
   SMTP_PORT=587
   SMTP_LOGIN=
   SMTP_KEY=
   SENDER_EMAIL=
   GROQ_API_KEY=
