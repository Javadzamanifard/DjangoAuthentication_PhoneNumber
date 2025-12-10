from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login

from accounts.models import CustomUser

from .services import send_sms


def login_signup_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number or len(phone_number) != 11 or not phone_number.isdigit():
            messages.error(request, 'شماره همراه معتبر نیست')
            return render(request, 'accounts/login_register.html')
        
        user, created = CustomUser.objects.get_or_create(
            phone_number=phone_number,
            defaults = {'username': phone_number}
        )
        otp = user.otp_generate()
        try:
            send_sms(phone_number, otp)
            messages.success(request, "کد تایید ارسال شد.")
            request.session['phone_number'] = phone_number
            return redirect('accounts:verify')
        except Exception as e:
            messages.error(request, "خطا در ارسال پیامک.")
            return render(request, 'accounts/login_register.html')
    return render(request, 'accounts/login_register.html')


def verify(request):
    phone_number = request.session.get('phone_number')
    if not phone_number:
        messages.error(request, 'لطفا شماره همراه خود را مجدداً وارد کنید.')
        return redirect('accounts:login_signup') 
    
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        messages.error(request, 'اطلاعات کاربر نامعتبر است.')
        return redirect('accounts:login_signup')
    
    if request.method == 'POST':
        code = request.POST.get('otp')
        
        if not code:
            messages.error(request, "کد تایید را وارد کنید.")
            return redirect('accounts:verify')
        
        if timezone.now() > user.otp_expiry:
            messages.error(request, 'کد تایید منقضی شده است دوباره تلاش کنید')
            return redirect('accounts:resend_otp')
        
        if code != user.otp_code:
            messages.error(request, 'کد تایید صحیح نیست.')
            return render(request, 'accounts/verify.html', {'phone_number': phone_number})
        
        user.is_phone_verified = True
        if 'phone_number' in request.session:
            del request.session['phone_number']
        user.save()
        login(request, user)
        messages.success(request, "ورود موفقیت‌آمیز بود.")
        return redirect('accounts:home') 
    return render(request, 'accounts/verify.html')


def resend_otp(request):
    phone_number = request.session.get('phone_number')
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        messages.error(request, 'کاربر نامعتبر.')
        return redirect('accounts:login_signup')
    
    otp = user.otp_generate()
    
    if user.otp_expiry and user.otp_expiry > timezone.now():
        minutes_left = (user.otp_expiry - timezone.now()).seconds // 60
        messages.warning(request, f"لطفاً صبر کنید. کد جدید تنها {minutes_left} دقیقه دیگر قابل ارسال است.")
        return redirect('accounts:verify')
    
    success = send_sms(phone_number, otp)
    if success:
        messages.success(request, f'کد تایید جدید به شماره {phone_number} ارسال شد.')
    else:
        messages.error(request, 'متأسفانه، در ارسال پیامک خطایی رخ داد. لطفا دوباره تلاش کنید.')
    return redirect('accounts:verify')


def home(request):
    if request.user.is_authenticated and request.user.is_phone_verified:
        return render(request, 'accounts/home.html')
    else:
        return redirect('accounts:login_signup')