from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import login
from django.core.exceptions import ValidationError

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        country = request.POST.get('country', '')
        city = request.POST.get('city', '')
        birthdate = request.POST.get('birthdate', '')
        avatar = request.FILES.get('avatar')

        # Basic validation
        if password1 != password2:
            return render(request, 'authapp/register.html', {'error': 'Passwords do not match'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            Profile.objects.create(user=user, country=country, city=city, birthdate=birthdate)
            login(request, user)
            return redirect('home')
        except ValidationError as e:
            return render(request, 'authapp/register.html', {'error': e.message})

    return render(request, 'authapp/register.html')
