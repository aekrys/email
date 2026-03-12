from django.shortcuts import render, redirect, get_object_or_404
from .models import Email
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


# Зарегистрироваться
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("inbox")
    else:
        form = UserCreationForm()

    template = "email_app/signup.html"
    context = {"form": form}

    return render(request, template, context)


# Входящие письма
@login_required
def inbox(request):
    emails = Email.objects.filter(user=request.user, folder="inbox")

    template = "email_app/inbox.html"
    context = {"emails": emails}

    return render(request, template, context)


# Отправленные письма
@login_required
def sent(request):
    emails = Email.objects.filter(user=request.user, folder="sent")

    template = "email_app/sent.html"
    context = {"emails": emails}

    return render(request, template, context)


# Архив
@login_required
def archive(request):
    emails = Email.objects.filter(user=request.user, folder="archive")

    template = "email_app/archive.html"
    context = {"emails": emails}

    return render(request, template, context)


# Корзина
@login_required
def trash(request):
    emails = Email.objects.filter(user=request.user, folder="trash")

    template = "email_app/trash.html"
    context = {"emails": emails}

    return render(request, template, context)


# Создать новое письмо
@login_required
def new_email(request):
    user = request.user
    template = "email_app/new_email.html"

    if request.method == "POST":
        sender = request.POST.get("sender")
        recipient = request.POST.get("recipient")
        topic = request.POST.get("topic")
        text = request.POST.get("text")

        Email.objects.create(
            user=user,
            sender=sender,
            recipient=recipient,
            topic=topic,
            text=text,
            folder="sent"
        )

        return redirect("sent")

    return render(request, template)


# Открыть письмо
@login_required
def open_email(request, pk):
    print(f"PK из URL: {pk}")
    email = get_object_or_404(Email, pk=pk, user=request.user)
    print(f"ID письма: {email.id}")

    if email.folder == "inbox" and not email.is_read:
        email.is_read = True
        email.save()

    template = "email_app/open_email.html"
    context = {"email": email}

    return render(request, template, context)


# Удалить письмо
@login_required
def delete_email(request, pk):
    email = get_object_or_404(Email, pk=pk, user=request.user)

    email.previous_folder = email.folder
    email.folder = "trash"
    email.save()

    return redirect("inbox")


# Восстановить письмо
@login_required
def restore_email(request, pk):
    email = get_object_or_404(Email, pk=pk, user=request.user)

    email.folder = email.previous_folder
    email.previous_folder = ""
    email.save()

    return redirect("trash")


# Отправить письмо в архив
@login_required
def archive_email(request, pk):
    email = get_object_or_404(Email, pk=pk, user=request.user)

    email.folder = "archive"
    email.save()

    return redirect("inbox")


# Выйти из аккаунта
def logout_view(request):
    logout(request)
    return redirect("login")