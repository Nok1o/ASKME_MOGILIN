import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseNotFound, HttpResponseServerError, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
import django.contrib.auth as auth

from app.ajax import HttpResponseAjaxError
from app.decorators import login_required_ajax
from app.models import Question, Answer, Tag, Profile, LikeQuestion, DislikeQuestion, LikeAnswer, DislikeAnswer
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

    limit = min(limit, MAX_LIMIT)

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

def render_with_tags_and_members(request, template_name, context):
    context['popular_tags'] = Tag.objects.get_popular_tags()
    context['best_members'] = Answer.objects.get_best_members()
    return render(request, template_name, context)

def index(request):
    page = paginate(request, Question.objects.get_new_questions())
    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render_with_tags_and_members(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page
    })

def hot_questions(request):
    page = paginate(request, Question.objects.get_best_questions())
    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render_with_tags_and_members(request, 'hot_questions.html', {
        'questions': page.object_list,
        'page_obj': page,
        'authorized': True
    })

def question(request, question_id):
    form = AnswerForm()
    question = get_object_or_404(Question, id=question_id)
    page = paginate(request, Answer.objects.get_answers_for_question(question))

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            form.save(question=question, user=request.user)
            return redirect(f'{reverse("question", args=[question.id])}?page={1}#answer-{form.get_answer_id()}')

    return render_with_tags_and_members(request, 'question.html', {
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
        'form': form,
        'user_is_author': request.user == question.author
    })

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

    return render_with_tags_and_members(request, 'tag_search.html', {
        'tag': tag,
        'questions': page.object_list,
        'page_obj': page
    })

@login_required
def ask(request):
    form = AskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        q = form.save(user=request.user)
        return redirect('question', question_id=q.id)

    return render_with_tags_and_members(request, 'ask.html', {'form': form})

def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = auth.authenticate(request, **form.cleaned_data)
        if user:
            auth.login(request, user)
            redirect_url = request.GET.get('next') or request.GET.get('continue') or DEFAULT_LOGIN_REDIRECT
            if redirect_url not in ['/', 'tag', 'ask', 'profile']:
                redirect_url = DEFAULT_LOGIN_REDIRECT
            return HttpResponseRedirect(redirect_url)
        else:
            form.add_error(None, 'Incorrect login or password')

    return render_with_tags_and_members(request, 'login.html', {'form': form})

def logout(request):
    auth.logout(request)
    referer = request.META.get('HTTP_REFERER', '/login/')
    return HttpResponseRedirect(referer)

def signup(request):
    form = UserForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        user = auth.authenticate(request, **form.cleaned_data)
        if user:
            auth.login(request, user)
        redirect_url = request.GET.get('continue', DEFAULT_SIGNUP_REDIRECT)
        if redirect_url not in ['/', 'tag', 'ask', 'profile']:
            redirect_url = DEFAULT_SIGNUP_REDIRECT
        return HttpResponseRedirect(redirect_url)

    return render_with_tags_and_members(request, 'signup.html', {'form': form})

@login_required
def settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = SettingsForm(request.POST or None, request.FILES or None, instance=request.user, profile_instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save(user_instance=request.user)
        messages.success(request, 'Profile updated successfully')

    return render_with_tags_and_members(request, 'settings.html', {'form': form})

@require_POST
@login_required_ajax
def question_feedback(request, question_id):
    return handle_feedback(request, Question, LikeQuestion, DislikeQuestion, question_id)

@require_POST
@login_required_ajax
def answer_feedback(request, answer_id):
    return handle_feedback(request, Answer, LikeAnswer, DislikeAnswer, answer_id)

@require_POST
@login_required_ajax
def correct_feedback(request, answer_id):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseAjaxError(code='error', message='Bad request')

    answer = get_object_or_404(Answer, id=answer_id)
    answer.is_correct = body.get('is_correct', False)
    answer.save()
    return JsonResponse(body)

def handle_feedback(request, model, like_model, dislike_model, object_id):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseAjaxError(code='error', message='Bad request')

    user = request.user
    obj = get_object_or_404(model, id=object_id)
    like_filter = like_model.objects.filter(**{model.__name__.lower(): obj, 'user': user})
    dislike_filter = dislike_model.objects.filter(**{model.__name__.lower(): obj, 'user': user})

    if body['type'] == 'like':
        if dislike_filter.exists():
            dislike_filter.delete()
            obj.num_likes += 1
        elif not like_filter.exists():
            like_model.objects.create(**{model.__name__.lower(): obj, 'user': user})
            obj.num_likes += 1

    elif body['type'] == 'dislike':
        if like_filter.exists():
            like_filter.delete()
            obj.num_likes -= 1
        elif not dislike_filter.exists():
            dislike_model.objects.create(**{model.__name__.lower(): obj, 'user': user})
            obj.num_likes -= 1

    obj.save()

    likes_count = like_model.objects.filter(**{model.__name__.lower(): obj}).count()
    dislike_count = dislike_model.objects.filter(**{model.__name__.lower(): obj}).count()

    return JsonResponse({'likes_count': likes_count - dislike_count})
