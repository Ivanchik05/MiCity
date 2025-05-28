import re

import requests
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import ContactMessage
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, LikeDislike
from django.views.decorators.http import require_POST, require_http_methods
import json
import logging
from django.views.decorators.http import require_GET
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "7259458746:AAFfT8A01NPfUVpNCSq2TzTBmHcGi3rF3yQ"
TELEGRAM_CHAT_ID = "907423155"


def about(request):
    return render(request, 'html/about.html')


def contact(request):
    return render(request, 'html/contact.html')


# @login_required
def index(request):
    posts = Post.objects.all().order_by('created_at')
    posts_data = []
    for post in posts:
        likes = post.likes_dislikes.filter(is_like=True).count()
        dislikes = post.likes_dislikes.filter(is_like=False).count()
        posts_data.append({
            'post': post,
            'likes': likes,
            'dislikes': dislikes,
        })
    return render(request, 'html/index.html', {'posts_data': posts_data})


def map(request):
    return render(request, 'html/map.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Сохраняем данные формы
        form_data = {
            'username': username,
        }

        # Словарь для ошибок
        errors = {}

        # Валидация имени пользователя
        if not username or not username.strip():
            errors['username'] = "Имя пользователя не может быть пустым."

        # Валидация пароля
        if not password or len(password) < 8:
            errors['password'] = "Пароль должен быть не менее 8 символов."

        # Если есть ошибки валидации, возвращаем форму
        if errors:
            print("Ошибки валидации логина:", errors)  # Отладка
            return render(request, 'html/login.html', {
                'errors': errors,
                'form_data': form_data
            })

        # Проверяем, существует ли пользователь
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            errors['general'] = "Неверное имя пользователя или пароль"
            print("Ошибка авторизации:", errors)  # Отладка
            return render(request, 'html/login.html', {
                'errors': errors,
                'form_data': form_data
            })

    return render(request, 'html/login.html', {'form_data': {}})


def logout(request):
    auth_logout(request)
    return redirect('login')


def success(request):
    return render(request, 'html/success.html')


def send_message(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not name or not email or not message:
            return render(request, 'html/contact.html', {
                'error': 'Все поля обязательны'
            })

        ContactMessage.objects.create(name=name, email=email, message=message)

        text = f"📩 *Новое сообщение с сайта:*\n\n👤 *Имя:* {name}\n📧 *Email:* {email}\n📝 *Сообщение:* {message}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            return redirect('success')
        else:
            return render(request, 'html/contact.html', {
                'error': 'Ошибка при отправке сообщения в Telegram'
            })

    return redirect('contact')


def register(request):
    if request.method == "POST":
        # Извлекаем данные из формы
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Сохраняем данные формы для отображения в случае ошибки
        form_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
        }

        # Словарь для хранения ошибок
        errors = {}

        # Валидация имени (должно начинаться с заглавной буквы, содержать только буквы, 2-20 символов)
        if not first_name or not re.match(r'^[A-ZА-Я][a-zа-я]{1,19}$', first_name):
            errors['first_name'] = "Имя должно начинаться с заглавной буквы и содержать только буквы (2-20 символов)."

        # Валидация фамилии (аналогично)
        if not last_name or not re.match(r'^[A-ZА-Я][a-zа-я]{1,19}$', last_name):
            errors[
                'last_name'] = "Фамилия должна начинаться с заглавной буквы и содержать только буквы (2-20 символов)."

        # Валидация email (должен содержать @)
        if not email or '@' not in email:
            errors['email'] = "Email должен содержать символ '@'."

        # Валидация логина (только буквы, 3-20 символов)
        if not username or not re.match(r'^[A-Za-z]{3,20}$', username):
            errors['username'] = "Логин должен содержать только буквы и быть от 3 до 20 символов."

        # Валидация пароля (не менее 8 символов)
        if not password or len(password) < 8:
            errors['password'] = "Пароль должен быть не менее 8 символов."

        # Валидация подтверждения пароля
        if password != confirm_password:
            errors['confirm_password'] = "Пароли не совпадают."

        # Проверяем, существует ли пользователь с таким логином
        if User.objects.filter(username=username).exists():
            errors['username_exists'] = "Пользователь с таким логином уже существует."

        # Если есть ошибки, возвращаем форму с ошибками
        if errors:
            print("Ошибки валидации регистрации:", errors)  # Отладка
            return render(request, 'html/register.html', {
                'errors': errors,
                'form_data': form_data
            })

        # Если валидация прошла, создаём пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        # Авторизуем пользователя после регистрации
        auth_login(request, user)
        return redirect('index')

    # Если запрос GET, просто отображаем форму
    return render(request, 'html/register.html', {'form_data': {}})



# @require_http_methods(["GET", "POST"])
@login_required
@require_POST
def toggle_like_dislike(request):
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        is_like = data.get('is_like')

        if post_id is None or is_like is None:
            return JsonResponse({'status': 'error', 'error': 'Invalid request data'}, status=400)

        post = Post.objects.get(id=post_id)
        user = request.user

        like_dislike, created = LikeDislike.objects.get_or_create(
            post=post,
            user=user,
            defaults={'is_like': is_like}
        )

        if not created:
            if like_dislike.is_like == is_like:
                like_dislike.delete()
            else:
                like_dislike.is_like = is_like
                like_dislike.save()

        likes = LikeDislike.objects.filter(post=post, is_like=True).count()
        dislikes = LikeDislike.objects.filter(post=post, is_like=False).count()

        logger.info(f"Sending WebSocket update for post {post_id}: likes={likes}, dislikes={dislikes}")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'posts',
            {
                'type': 'like_dislike_update',
                'update': {
                    'post_id': str(post_id),
                    'likes': likes,
                    'dislikes': dislikes
                }
            }
        )

        return JsonResponse({'status': 'ok', 'likes': likes, 'dislikes': dislikes})
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Post not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in toggle_like_dislike: {str(e)}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)