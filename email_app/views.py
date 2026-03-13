from django.shortcuts import render, redirect, get_object_or_404
from .models import Email
from django.contrib.auth.forms import UserCreationForm  # Встроенная форма для регистрации
from django.contrib.auth.models import User  # Встроенная модель пользователя
from django.contrib.auth import login, logout  # Функции для авторизации
from django.contrib.auth.decorators import login_required  # Декоратор для проверки авторизации пользователя


def signup(request):
    """
    Функция для регистрации нового пользователя

    При отправке пользователем формы проверяет
    данные на корректность, сохраняет нового пользователя
    в базе данных, направляет на главную (страница с входящими)
    """

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


@login_required
def inbox(request):
    """
    Функция для входящих писем

    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Отображает все входящие письма пользователя
    """

    emails = Email.objects.filter(user=request.user, folder="inbox")

    template = "email_app/inbox.html"
    context = {"emails": emails}

    return render(request, template, context)


@login_required
def sent(request):
    """
    Функция для отправленных писем

    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Отображает все отправленные письма пользователя
    """

    emails = Email.objects.filter(user=request.user, folder="sent")

    template = "email_app/sent.html"
    context = {"emails": emails}

    return render(request, template, context)


@login_required
def archive(request):
    """
    Функция для архива

    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Отображает все архивированные письма пользователя
    """

    emails = Email.objects.filter(user=request.user, folder="archive")

    template = "email_app/archive.html"
    context = {"emails": emails}

    return render(request, template, context)


@login_required
def trash(request):
    """
    Функция для корзины

    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Отображает все удаленные письма пользователя
    """

    emails = Email.objects.filter(user=request.user, folder="trash")

    template = "email_app/trash.html"
    context = {"emails": emails}

    return render(request, template, context)


@login_required
def new_email(request):
    """
    Функция для создания нового письма

    Направляет неавторизованного пользователя на страницу входа в аккаунт
    При отправке пользователем формы email отправителя 
    принимает вид username@email
    Проверяет формат email получателя и существование этого пользователя
    При наличии такого получателя, отправляет письмо
    Письмо появляется в папке "Отправленные" у отправителя, 
    в папке "Входящие" - у получателя
    """

    user = request.user
    template = "email_app/new_email.html"

    if request.method == "POST":
        sender = f"{request.user.username}@email"
        recipient = request.POST.get("recipient")

        if recipient.endswith("@email"):
            recipient_username = recipient.replace("@email", "")
        else:
            template = "email_app/new_email.html"
            context = {"error": "Имя получателя должно иметь формат username@email"}
            return render(request, template, context)

        try:
            recipient_user = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            template = "email_app/new_email.html"
            context = {"error": "Пользователя с таким email не существует"}
            return render(request, template, context)

        topic = request.POST.get("topic")
        text = request.POST.get("text")

        # Письмо ля отправителя
        Email.objects.create(
            user=user,
            sender=sender,
            recipient=recipient,
            topic=topic,
            text=text,
            folder="sent"
        )

        # Письмо для получателя
        Email.objects.create(
            user=recipient_user,
            sender=sender,
            recipient=recipient,
            topic=topic,
            text=text,
            folder="inbox"
        )

        return redirect("sent")

    return render(request, template)


@login_required
def open_email(request, pk):
    """
    Функция для просмотра письма
    
    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Открывает выбранное пользователем письмо
    Если письмо во "Входящих" и еще не прочитано, помечается как прочитанное
    """

    print(f"PK из URL: {pk}")
    email = get_object_or_404(Email, pk=pk, user=request.user)
    print(f"ID письма: {email.id}")

    if email.folder == "inbox" and not email.is_read:
        email.is_read = True
        email.save()

    template = "email_app/open_email.html"
    context = {"email": email}

    return render(request, template, context)


@login_required
def delete_email(request, pk):
    """
    Функция для удаления письма
    
    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Удаляет выбранное пользователем письмо
    Запоминает папку, из которой удалялось письмо,
    чтобы в случае восстановления оно вернулось туда же
    """

    email = get_object_or_404(Email, pk=pk, user=request.user)

    email.previous_folder = email.folder
    email.folder = "trash"
    email.save()

    return redirect("inbox")


@login_required
def restore_email(request, pk):
    """
    Функция для восстановления письма из удаленных
    
    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Восстанавливает письмо, возвращая в ту папку, откуда оно было удалено
    """

    email = get_object_or_404(Email, pk=pk, user=request.user)

    email.folder = email.previous_folder
    email.previous_folder = ""
    email.save()

    return redirect("trash")


@login_required
def archive_email(request, pk):
    """
    Функция для отправления письма в архив
    
    Направляет неавторизованного пользователя на страницу входа в аккаунт
    Отправляет выбранное пользователем письмо в архив
    """

    email = get_object_or_404(Email, pk=pk, user=request.user)

    email.folder = "archive"
    email.save()

    return redirect("inbox")


def logout_view(request):
    """
    Функция для выхода из аккаунта

    После выхода пользователя из аккаунта
    перекидывает на страницу входа в аккаунт
    """

    logout(request)
    return redirect("login")
