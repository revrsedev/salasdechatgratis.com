from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.images import get_image_dimensions
from django.urls import reverse
from django.contrib import messages
import os
from django.conf import settings
from django.http import HttpResponse, Http404


VALID_COUNTRIES = ['US', 'FR', 'DE', 'ES', 'IT', 'GB', 'CA', 'AU', 'NZ', 'IN', 'BR']  # Example list

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        country = request.POST.get('country', '').strip().upper()  # Convert to uppercase for consistency
        city = request.POST.get('city', '').strip()
        birthdate = request.POST.get('birthdate', '')
        avatar = request.FILES.get('avatar')

        form_data = {
            'username': username,
            'email': email,
            'country': country,
            'city': city,
            'birthdate': birthdate
        }

        if password1 != password2:
            return render(request, 'authapp/register.html', {'error': 'Las contraseñas no coinciden.', 'form_data': form_data})
        if len(username) < 3 or len(username) > 30:
            return render(request, 'authapp/register.html', {'error': 'El nombre de usuario debe tener entre 3 y 30 caracteres.', 'form_data': form_data})
        if User.objects.filter(username=username).exists():
            return render(request, 'authapp/register.html', {'error': 'Este nombre de usuario ya está tomado.', 'form_data': form_data})
        if User.objects.filter(email=email).exists():
            return render(request, 'authapp/register.html', {'error': 'Correo electrónico ya está en uso.', 'form_data': form_data})

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'authapp/register.html', {'error': 'Dirección de correo electrónico no válida.', 'form_data': form_data})

        if country not in VALID_COUNTRIES:
            return render(request, 'authapp/register.html', {'error': 'País no válido.', 'form_data': form_data})

        if avatar:
            try:
                width, height = get_image_dimensions(avatar)
                if avatar.size > 2 * 1024 * 1024:
                    return render(request, 'authapp/register.html', {'error': 'El tamaño del archivo de avatar debe ser inferior a 2 MB.', 'form_data': form_data})
                if width > 500 or height > 500:
                    return render(request, 'authapp/register.html', {'error': 'Las dimensiones del avatar deben ser 500x500 píxeles o menos', 'form_data': form_data})
            except Exception:
                return render(request, 'authapp/register.html', {'error': 'El archivo cargado no es una imagen válida', 'form_data': form_data})

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            profile = Profile(user=user, country=country, city=city, birthdate=birthdate, avatar=avatar)
            profile.save()
            login(request, user)
            return redirect('home')
        except ValidationError as e:
            return render(request, 'authapp/register.html', {'error': str(e), 'form_data': form_data})
        except Exception as e:
            return render(request, 'authapp/register.html', {'error': 'Ocurrió un error al crear el perfil. Por favor, inténtelo de nuevo.', 'form_data': form_data})

    return render(request, 'authapp/register.html')

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'authapp/profile.html', {'profile': profile})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        profile = Profile.objects.get(user=user)
        
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        country = request.POST.get('country', '').strip()
        city = request.POST.get('city', '').strip()
        birthdate = request.POST.get('birthdate', '')
        avatar = request.FILES.get('avatar')
        
        try:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                raise ValidationError('Username already taken.')
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                raise ValidationError('Email already in use.')
            
            user.username = username
            user.email = email
            user.save()
            
            profile.country = country
            profile.city = city
            profile.birthdate = birthdate
            
            if avatar:
                width, height = get_image_dimensions(avatar)
                if avatar.size > 2 * 1024 * 1024:
                    raise ValidationError('Avatar file size should be less than 2MB.')
                if width > 500 or height > 500:
                    raise ValidationError('Avatar dimensions should be 500x500 pixels or less.')
                profile.avatar = avatar
            
            profile.save()
            return redirect('profile')
        except ValidationError as e:
            return render(request, 'authapp/profile.html', {'profile': profile, 'error': str(e)})
    
    return redirect('profile')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the profile page after successful login
            return redirect(reverse('profile'))  # or use '/auth/profile/' directly
        else:
            # Invalid login credentials
            messages.error(request, 'Invalid username or password.')
            return render(request, 'authapp/login.html')
    else:
        return render(request, 'authapp/login.html')
    
@login_required
def profile_view(request):
    # Assuming 'profile.html' is your template for displaying user profiles
    return render(request, 'authapp/profile.html')

def avatar_view(request, username):
    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, f'{username}.png')
    
    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/png")
    else:
        raise Http404("Avatar not found")