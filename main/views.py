import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from main.forms import LoginForm, AddSnippetForm
from main.models import Snippet
from django.utils.html import escape
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from django.utils.html import strip_tags
from django.http import HttpResponse



def get_base_context(request, pagename):
    return {
        'pagename': pagename,
        'loginform': LoginForm(),
        'user': request.user,
    }


def index_page(request):
    context = get_base_context(request, 'PythonBin')
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    context = get_base_context(request, 'Добавление нового сниппета')
    if request.method == 'POST':
        addform = AddSnippetForm(request.POST)
        if addform.is_valid():
            record = Snippet(
                name=addform.data['name'],
                code=addform.data['code'],
                creation_date=datetime.datetime.now(),
            )
            record.user = context['user']
            record.save()
            id = record.id

            context['addform'] = AddSnippetForm(
                initial={
                    'user': str(context['user']),
                }
            )

            messages.add_message(request, messages.SUCCESS, "Сниппет успешно добавлен")
            redirect('view_snippet', id=id)
            return render(request, 'pages/add_snippet.html', context)

        else:
            messages.add_message(request, messages.ERROR, "Некорректные данные в форме")
            return redirect('add_snippet')
    else:
        h = context['user']
        context['addform'] = AddSnippetForm(
            initial={
                'user': str(h),
            }
        )
    return render(request, 'pages/add_snippet.html', context)


def view_snippet_page(request, id):
    context = get_base_context(request, 'Просмотр сниппета')
    try:
        record = Snippet.objects.get(id=id)
        code = (highlight(record.code, PythonLexer(), HtmlFormatter()))

        context['addform'] = AddSnippetForm(
            {
                'user': str(record.user),
                'name': record.name,
            }
        )

        context['code']=record.code
    except Snippet.DoesNotExist:
        raise Http404
    return render(request, 'pages/view_snippet.html', context)


def login_page(request):
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.data['username']
            password = loginform.data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, "Авторизация успешна")
            else:
                messages.add_message(request, messages.ERROR, "Неправильный логин или пароль")
        else:
            messages.add_message(request, messages.ERROR, "Некорректные данные в форме авторизации")
    return redirect('index')


def logout_page(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Вы успешно вышли из аккаунта")
    return redirect('index')


def my_snippets_page(request):
    context = get_base_context(request, 'Мои сниппеты')
    if context['user']!='l':
        record = Snippet.objects.all()
        context['addform'] = []
        for i in record:
            initial={
                    'user': str(i.user),
                    'name': i.name ,
                    'id': str(i.id),
                    'date': str(i.creation_date).split('.')[0]
            }
            if initial['user']=='vasya':
                context['addform'] += [{'name':initial['name'],'date':initial['date'], 'id':initial['id']}]



        return render(request, 'pages/my_page.html', context)

    else:
        return redirect('index')
