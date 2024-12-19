from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseNotFound, HttpResponseServerError, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
import django.contrib.auth as auth

from app.models import Question, Answer, Tag, Profile
from app.forms import LoginForm, UserForm, SettingsForm, AskForm, AnswerForm

DEFAULT_QUESTIONS_PER_PAGE = 5
DEFAULT_LIMIT = 10
MAX_LIMIT = 50
DEFAULT_PAGE = 1
DEFAULT_LOGIN_REDIRECT = '/profile/edit'
DEFAULT_SIGNUP_REDIRECT = '/'


def paginate(request, query_set):
    try:
        limit = int(request.GET.get('limit', DEFAULT_LIMIT))
    except ValueError:
        limit = DEFAULT_LIMIT

    if limit > MAX_LIMIT:
        limit = DEFAULT_LIMIT

    try:
        num_page = int(request.GET.get('page', DEFAULT_PAGE))
    except ValueError:
        raise Http404

    paginator = Paginator(query_set, limit)
    try:
        page = paginator.page(num_page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def index(request):
    page = paginate(request, Question.objects.get_new_questions())

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'index.html',
        context={
            'questions': page.object_list, 'popular_tags': Tag.objects.get_popular_tags(),
            'page_obj': page
        }
    )


def hot_questions(request):
    page = paginate(request, Question.objects.get_best_questions())

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'hot_questions.html',
        context={
            'questions': page.object_list, 'page_obj': page,
            'popular_tags': Tag.objects.get_popular_tags(), 'authorized': True}
    )


def question(request, question_id):
    form = AnswerForm()
    question = get_object_or_404(Question, id=question_id)
    page = paginate(request,
                    Answer.objects.get_answers_for_question(question))

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            form.save(question=question, user=request.user)

            return redirect(f'{reverse("question", args=[question.id])}?page={1}#answer-{form.get_answer_id()}')

    return render(
        request, 'question.html',
        context={'question': question, 'popular_tags': Tag.objects.get_popular_tags(), 'answers': page.object_list,
                 'page_obj': page, 'form': form}
    )


def tag(request, tag_name):
    try:
        tag = Tag.objects.get(tag_name=tag_name)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("The tag you are trying to find does not exist")
    except MultipleObjectsReturned:
        return HttpResponseServerError("Found more than 1 instance of the tag. Report tag id to the admin.")

    page = paginate(request, Tag.objects.get_questions(tag))

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'tag_search.html',
        context={
            'popular_tags': Tag.objects.get_popular_tags(), 'tag': tag,
            'questions': page.object_list, 'page_obj': page
        }
    )


@login_required
def ask(request):
    form = AskForm()
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            q = form.save(user=request.user)
            return redirect('question', question_id=q.id)

    return render(
        request, 'ask.html',
        context={'popular_tags': Tag.objects.get_popular_tags(), 'form': form}
    )


def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)

                redirect = request.GET.get('next')
                if redirect is None:
                    redirect = request.GET.get('continue')
                    if redirect is None or (redirect != '/' and 'tag' not in redirect
                                            and 'ask' not in redirect and 'profile' not in redirect):
                        redirect = DEFAULT_LOGIN_REDIRECT
                return HttpResponseRedirect(redirect)
            else:
                form.add_error(None, 'Incorrect login or password')
                form.add_error('username', "")
                form.add_error('password', "")

    return render(
        request, 'login.html',
        context={'popular_tags': Tag.objects.get_popular_tags(), 'form': form}
    )


def logout(request):
    auth.logout(request)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect('/login/')


def signup(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
            redirect = request.GET.get('continue')
            if redirect is None or (redirect != '/' and 'tag' not in redirect
                                    and 'ask' not in redirect and 'profile' not in redirect):
                redirect = DEFAULT_SIGNUP_REDIRECT
            return HttpResponseRedirect(redirect)

    return render(
        request, 'signup.html',
        context={'popular_tags': Tag.objects.get_popular_tags(), 'form': form}
    )


@login_required
def settings(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=user, profile_instance=profile)
        if form.is_valid():
            form.save(user_instance=user)
            messages.success(request, 'Profile updated successfully')
    else:
        form = SettingsForm(instance=user, profile_instance=profile)

    return render(request, 'settings.html', {
        'form': form,
        'popular_tags': Tag.objects.get_popular_tags(),
    })
