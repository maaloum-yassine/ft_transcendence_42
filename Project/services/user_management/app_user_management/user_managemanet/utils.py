import smtplib, requests , os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jwt, random, string , hashlib
from django.utils import timezone
from django.conf import settings


class PasswordValidationError(Exception):
    pass




def send_code(to_email, verification_code, name_user):
    msg = MIMEMultipart()
    msg['From'] = 'maaloum.yassine@gmail.com'
    msg['To'] = to_email
    msg['Subject'] = 'Vérification de votre compte'
    body = (
       f"Dear user {name_user},\n\n"
        "Thank you for attempting to log in to your account.\n\n"
        "To finalize your login, please enter the verification code below:\n\n"
        f"Verification Code: {verification_code}\n\n"
        "Best regards,\n"
        "The Support Team."
    )
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  
            server.login('maaloum.yassine@gmail.com', settings.EMAIL_PASSWORD)  # Authentification
            server.send_message(msg) 
            print('Email envoyé avec succès.')
    except Exception as e:
        print(f"Échec de l'envoi de l'email : {e}")


def send_email(to_email, html_message, check):
    print("SEND EMAILLLLLLL")
    from_email = 'maaloum.yassine@gmail.com'
    password = settings.EMAIL_PASSWORD
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    if check is True:
        msg['Subject']  = 'Resetting your password'
    else :
        msg['Subject'] = 'Activate your account'
    msg.attach(MIMEText(html_message, 'html'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, [to_email], msg.as_string())
            print('Email envoyé avec succès.')
    except Exception as e:
        print(f'Erreur lors de l\'envoi de l\'email : {e}')


def generate_token(user, tmp):
    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'active_2fa': user.active_2fa,
    }
    print("/*/*/IM HERE TOKEN*/*/*/*")
    if  tmp is True:
        expiration_time = timezone.timedelta(days=1)
    else:
        expiration_time = timezone.timedelta(minutes=5)
    payload['exp'] = timezone.now() + expiration_time
    return (jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256'))


def generate_random(length=8):
    characters = '0123456789' 
    raw_code = ''.join(random.choice(characters) for _ in range(length))
    hashed_code = hashlib.sha256(raw_code.encode()).hexdigest()
    return hashed_code, raw_code


def verify_code(input_code, user_code):
    hashed_input_code = hashlib.sha256(input_code.encode()).hexdigest()
    return hashed_input_code == user_code

def   validate_passwords(passowrd, confirm_password):
    if len(passowrd) < 4:
        raise PasswordValidationError("Password must contain at least 4 characters.")
    if not any(char.isdigit() for char in passowrd):
        raise PasswordValidationError("Le mot de passe doit contenir au moins un chiffre.")
    if not any(char.isupper() for char in passowrd):
        raise PasswordValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
    if passowrd != confirm_password:
        raise PasswordValidationError("Les mots de passe ne correspondent pas.")


def return_image(avatar_path):
    avatar_path = os.path.join(settings.MEDIA_ROOT , avatar_path)
    if not os.path.exists(avatar_path):
        return False
    return True



