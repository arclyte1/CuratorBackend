import random
import smtplib
from email.mime.text import MIMEText
import os

import redis

from CuratorBackend.settings import MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

r = redis.StrictRedis(
    host=os.environ.get("REDIS_HOST"),
    port=int(os.environ.get("REDIS_PORT"))
)


def __can_send_code(email: str) -> bool:
    return not bool(r.exists(email + "CANT_SEND_CODE"))


def __generate_code(email: str) -> str:
    code = f"{random.randint(0, 9999):04d}"
    r.set(email, code)
    r.expire(email, 600)
    r.set(email + "CANT_SEND_CODE", 1)
    r.expire(email + "CANT_SEND_CODE", 29)
    return code


def send_code(email: str) -> bool:
    if __can_send_code(email):
        code = __generate_code(email)
        smtp = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
        msg = MIMEText(f"""Ваш код подтверждения {code}. Код действует 10 минут.""")
        msg["Subject"] = "Код подтверждения"
        msg["To"] = email
        msg["From"] = MAIL_USERNAME
        smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        smtp.quit()
        return True
    else:
        return False


def verify_code(email: str, code: str) -> bool:
    if r.exists(email):
        print(r.get(email).decode())
        return r.get(email).decode() == code
    else:
        return False
