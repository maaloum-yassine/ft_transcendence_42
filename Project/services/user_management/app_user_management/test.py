import smtplib
from email.message import EmailMessage

def send_test_email():
    msg = EmailMessage()
    msg.set_content("Ceci est un e-mail de test.")
    msg['Subject'] = "Test Email"
    msg['From'] = "maaloum.yassine@gmail.com"  # Remplacez par votre adresse e-mail
    msg['To'] = "maaloum.yassine@gmail.com"  # Remplacez par l'adresse e-mail du destinataire

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("maaloum.yassine@gmail.com", "ygvb hzpx ikea kkha")
            server.send_message(msg)
            print("E-mail envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail: {e}")

send_test_email()
