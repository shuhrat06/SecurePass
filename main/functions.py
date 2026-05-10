import string
from random import choice, shuffle, sample
import hashlib
import requests
import os
import smtplib
import dotenv
from groq import Groq

dotenv.load_dotenv()

lowercases = list(string.ascii_lowercase)    
uppercases = list(string.ascii_uppercase)     
numbers = list(string.digits)                  
punctuations = list(string.punctuation) 

def generate_password(
        length: int,
        lowercase,
        uppercase,
        number,
        punctuation
        ):
    
    characters=[]
    password=[]

    if lowercase=="on":
        characters.append(lowercases)
    if uppercase=="on":
        characters.append(uppercases)
    if number=="on":
        characters.append(numbers)
    if punctuation=="on":
        characters.append(punctuations)

    if not characters:
        return ""
    
    k=length//len(characters)
    for collection in characters:
        password+=sample(collection,k=k)
    shuffle(password)
    
    for i in range(len(password),length):
        belgi_turi=choice(characters)
        password.append(choice(belgi_turi))
    shuffle(password)
    password="".join(password)
    return password



COMMON_PASSWORDS = {
    'password', '123456', '12345678', 'qwerty', 'abc123',
    'admin', 'welcome', 'login', 'password123', 'admin123',
    '12345', '123456789', '111111', '123123', '000000',
    'qwerty123', '1q2w3e', 'qwertyuiop', 'asdfgh', 'zxcvbn',
    'iloveyou', 'sunshine', 'princess', 'dragon', 'password1',
    '1234567', '1234567890', 'qwerty1', 'abc12345', 'football',
    'monkey', 'shadow', 'master', 'hello', 'freedom',
    'whatever', 'trustno1', 'batman', 'superman', 'michael',
    'jennifer', 'jordan', 'hunter', 'thomas', 'robert',
    'matrix', 'computer', 'internet', 'security', 'python'
}


def in_common_passwords(password):
    with open('main/common_passwords.txt') as passwords:
        for p in passwords:
            if password == p.strip():
                return True
        return False


def check_pwned_password(password):
    """
    Parol haveibeenpwned.com bazasida bormi tekshiradi
    Return: (count, message)
    """
    try:
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        response = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=5,
            headers={'User-Agent': 'Password-Checker/1.0'}
        )
        
        if response.status_code == 200:
            for line in response.text.splitlines():
                line_suffix, count = line.split(':')
                if line_suffix == suffix:
                    return int(count), f"Bu parol buzilgan bazalarda {count} marta uchragan!"
        return 0, "Parol buzilgan bazalarda topilmadi."
    except:
        return -1, "Buzilgan bazalar bilan bog'lanib bo'lmadi."


def check_password(password):
    ball = 0
    
    result = {
        'count': {
            'uppercase': 0,
            'lowercase': 0,
            'chars': 0,
            'numbers': 0
        },
        'rate': {
            "char_type": {
                "count": 0,
                'score': 0
            },
            "repeat": {
                "repeat_persentage": 0,
                'score': 0
            },
            "length": {
                'length': 0,
                'score': 0
            },
            "total": 0
        },
        'feedback': "",
        'security_checks': {
            'is_common': False,
            'is_pwned': False,
            'pwned_count': 0,
            'warning_message': ""
        }
    }
    
    # Bo'sh parol tekshiruvi
    if not password or len(password) == 0:
        result['feedback'] = "Weak"
        result['rate']['total'] = 0
        result['security_checks']['warning_message'] = "Parol kiritilmagan!"
        return result
    
    # ========== BELGI TURINI ANIQLASH ==========
    belgi_turi = {
        "kich_harf": 0,
        "kat_harf": 0,
        "son": 0,
        "belgi": 0
    }
    
    # 1. HARFLARNI SANASH
    for i in password:
        if i in lowercases:
            belgi_turi["kich_harf"] = 1
            result["count"]['lowercase'] += 1
        elif i in uppercases:
            belgi_turi["kat_harf"] = 1
            result["count"]['uppercase'] += 1
        elif i in numbers:
            belgi_turi["son"] = 1
            result["count"]['numbers'] += 1
        elif i in punctuations:
            belgi_turi["belgi"] = 1
            result["count"]['chars'] += 1
    
    # 2. HARF TURLARI BALLI
    xil = sum(belgi_turi.values())
    if xil == 4:
        ball = 50
        result["rate"]["char_type"]["count"] = 4
        result["rate"]["char_type"]["score"] = 50
    elif xil == 3:
        ball = 30
        result["rate"]["char_type"]["count"] = 3
        result["rate"]["char_type"]["score"] = 30
    elif xil == 2:
        ball = 10
        result["rate"]["char_type"]["count"] = 2
        result["rate"]["char_type"]["score"] = 10
    elif xil == 1:
        ball = 5
        result["rate"]["char_type"]["count"] = 1
        result["rate"]["char_type"]["score"] = 5
    
    # 3. TAKRORLANISH BALLI
    password_len = len(password)
    if password_len > 0:
        n = (len(set(password)) / password_len) * 100
    else:
        n = 0
    
    result["rate"]["repeat"]["repeat_persentage"] = n
    
    if n >= 50 and n < 70:
        score = (n - 49) * 0.15
    elif n >= 70 and n < 80:
        score = 3 + (n - 69) * 0.4
    elif n >= 80 and n < 90:
        score = 7 + (n - 79) * 0.5
    elif n >= 90 and n <= 100:
        score = 13 + (n - 89) * (7 / 11)
    else:
        score = 0
    
    ball += score
    result["rate"]["repeat"]["score"] = round(score, 2)
    
    # 4. UZUNLIK BALLI
    n = password_len
    if n < 5:
        score = 0
    elif n >= 5 and n < 8:
        score = (10 / 3) * (n - 4)
    elif n >= 8 and n <= 10:
        score = 10 + (11 / 3) * (n - 7)
    elif n >= 11 and n <= 14:
        score = 21 + (14 / 4) * (n - 10)
    else:
        score = 35
    
    result["rate"]["length"]["score"] = round(score, 2)
    result["rate"]["length"]["length"] = n
    ball += score
    
    # ========== XAVFSIZLIK TEKSHIRUVLARI ==========
    warning_messages = []
    penalty = 0
    
    # 5. KENG TARQALGAN PAROLLAR TEKSHIRUVI
    if in_common_passwords(password):
        result['security_checks']['is_common'] = True
        penalty += 20
        warning_messages.append("⚠️ Bu juda keng tarqalgan parol! Birinchi bo'lib sinab ko'riladi.")
    
    # 6. BUZILGAN BAZALAR TEKSHIRUVI
    try:
        pwned_count, pwned_msg = check_pwned_password(password)
        if pwned_count > 0:
            result['security_checks']['is_pwned'] = True
            result['security_checks']['pwned_count'] = pwned_count
            penalty += min(30, pwned_count // 10)
            warning_messages.append(f"⚠️ {pwned_msg}")
        elif pwned_count == -1:
            warning_messages.append("ℹ️ Buzilgan bazalar bilan bog'lanib bo'lmadi (internet yo'q)")
    except:
        warning_messages.append("ℹ️ Buzilgan bazalar tekshiruvi o'tkazilmadi")
    
    # Ballga jarima qo'llash
    ball = max(0, ball - penalty)
    
    # Xavfsizlik ogohlantirishlarini birlashtirish
    result['security_checks']['warning_message'] = " | ".join(warning_messages) if warning_messages else "✅ Xavfsizlik tekshiruvlaridan o'tdi"
    
    # UMUMIY BALLNI SAQLASH
    result["rate"]["total"] = round(ball, 2)
    
    # 7. FEEDBACK
    if ball <= 30:
        result["feedback"] = "Kuchsiz"
        if result['security_checks']['is_common'] or result['security_checks']['is_pwned']:
            result["feedback"] = "Kuchsiz (Xavfli)"
    elif ball <= 60:
        result["feedback"] = "O'rtacha kuchlilik"
    elif ball <= 85:
        result["feedback"] = "Kuchli"
    else:
        result["feedback"] = "Juda kuchli"

    
    return result


def send_email(user, confirm_code, header_msg):

    domain = os.environ.get('SMTP_DOMAIN')
    port = os.environ.get('SMTP_PORT')
    login = os.environ.get('SMTP_LOGIN')
    smtp_key = os.environ.get('SMTP_KEY')
    sender_email = os.environ.get('SENDER_EMAIL')
    receiver_email = user.email
    # receiver_email = user



    message = (
        f"From: SecurePass <{sender_email}>\n"
        f"To: {receiver_email}\n"
        "Subject: Confirmation\n\n"
        f"Salom, xurmatli {receiver_email}\n"
        f"{header_msg} tasdiqlash parolingiz: {confirm_code}\n"
    )

    server = smtplib.SMTP(
        domain,
        port
    )
    try:
        server.starttls()
        server.login(login, smtp_key)
        server.sendmail(
            sender_email,
            receiver_email,
            message
        )
    except Exception as e:
        print(e)



SCHEMA_DESCRIPTION = """
You will receive a structured JSON object called "result" which contains password security analysis data generated by a local system.

You MUST understand the meaning of each field before performing analysis.

Max rate: 105
Min rate: 0

========================================
1. COUNT SECTION (Character Statistics)
========================================
"count" contains raw character statistics of the password:

- uppercase: number of uppercase letters (A-Z)
- lowercase: number of lowercase letters (a-z)
- chars: total number of all characters in the password
- numbers: number of numeric digits (0-9)

========================================
2. RATE SECTION (Scoring System)
========================================
"rate" contains evaluation scores of different security aspects:

- char_type:
    - count: number of character types used
    - score: higher = better security

- repeat:
    CRITICAL INTERPRETATION RULE (MUST FOLLOW EXACTLY):
    - repeat_persentage is NOT "repetition level"
    - IT IS "uniqueness level"
    - HIGH value = MORE UNIQUE characters = GOOD security
    - LOW value = MORE repetition/patterns = BAD security
    - DO NOT apply standard percentage logic here
    - score: higher score = better uniqueness and better security

- length:
    - length: total password length
    - score: higher = better security

- total:
    overall security score

========================================
3. SECURITY CHECKS SECTION
========================================
- is_common: True means extremely weak password
- is_pwned: True means critical security risk (data breach exposure)
- pwned_count: number of times found in leaks

========================================
IMPORTANT RULES:
- ALWAYS follow the CUSTOM meaning of repeat_persentage above
- NEVER interpret it as standard repetition metric
"""


def get_feedback_from_ai(result):
    
    command = f"""
You are a senior cybersecurity expert and enterprise-level password security auditor.

You perform password audits based on international standards:
- NIST SP 800-63B (Digital Identity Guidelines)
- OWASP Authentication Cheat Sheet
- ISO/IEC 27001 security practices

You are given a password evaluation result from a local system.

{SCHEMA_DESCRIPTION}

INPUT:
{result}

STRICT RULES:
- ALWAYS start response with: "Salom"
- NEVER say "Xaridorga salom"
- NEVER start with formal customer greeting
- Be direct and professional

TASK:
- Perform a fair and realistic security audit of the password.
- Be objective: do NOT exaggerate weaknesses and do NOT overpraise strength.
- Evaluate the password honestly based on security principles.

IMPORTANT BEHAVIOR RULES:
- If the password is strong, acknowledge it clearly and positively.
- If the password is medium, balance strengths and weaknesses.
- If the password is weak, clearly explain risks and urgency.
- Always include constructive improvement advice, even for strong passwords.
- Maintain a professional but encouraging tone (like a real security consultant).

SECURITY ANALYSIS REQUIREMENTS:
- Consider entropy, length, complexity, and predictability
- Mention relevant standards (NIST SP 800-63B, OWASP) when applicable
- Identify realistic attack risks only if they truly apply
- Do NOT fabricate or overstate weaknesses

RESPONSE STYLE:
- Respond ONLY in Uzbek language (Latin alphabet)
- Use a professional cybersecurity consultant tone
- Use natural paragraphs (no JSON, no markdown)
- Be moderately detailed, not overly long, not overly short
- Avoid repetitive or exaggerated warnings

GOAL:
Provide a fair, realistic, and human-like cybersecurity audit that reflects both strengths and risks of the password.
"""
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": command,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content
