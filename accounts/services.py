import kavenegar
from environs import Env

env = Env()
env.read_env()
KAVENEGARAPI = env.str('KAVENEGARAPI')
SENDER = env.str('SENDER')


def send_sms(receptor, message):
    """
    ارسال پیامک از طریق کاوه‌نگار
    """
    try:
        api = kavenegar.KavenegarAPI(KAVENEGARAPI)
        params = {
            'sender': SENDER,  
            'receptor': receptor,  
            'message': message
        }
        response = api.sms_send(params)
        return True
    except Exception as e:
        print(f"خطا در ارسال پیامک: {e}")
        return False