import smtplib
import random
# dqay wkmz ayho tzsf

app_password = "dqay wkmz ayho tzsf"

def send_gmail(gmail_user, recipient_email, message):
    gmail_user = gmail_user
    recipient_email = recipient_email
    message = message

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_user, app_password)
        server.sendmail(gmail_user, recipient_email, message)
        server.quit()
        return "Xabar muvaffaqiyatli yuborildi!"
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"


# print(send_gmail(gmail_user="shohruh.abd2223@gmail.com",
#                  recipient_email="shohruh.abd0823@gmail.com",
#                  message="Hello"))