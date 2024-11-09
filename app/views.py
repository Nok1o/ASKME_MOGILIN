import copy
import random

from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.shortcuts import render

from app.models import Question, Answer, Tag, DEFAULT_POPULAR_TAGS_NUM

# Create your views here.

QUESTIONS = Question.objects.all()

ANSWERS = Answer.objects.all()

TAGS = Tag.objects.all()

AMOUNT_POPULAR_TO_SHOW = 5


def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')

    try:
        page_num = int(page_num) if page_num else 1
    except ValueError:
        return None

    if page_num > (len(objects_list) - 1) // per_page + 1 or page_num < 1:
        return None

    paginator = Paginator(objects_list, per_page)
    page = paginator.page(page_num)

    return page


def index(request):
    page = paginate(QUESTIONS, request)

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'index.html',
        context={
            'questions': page.object_list, 'popular_tags': Tag.objects.get_popular_tags(),
            'page_obj': page, 'authorized': True
        }
    )


def hot_questions(request):
    hot_qs = Question.objects.order_by('-num_likes')

    page = paginate(hot_qs, request)

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'hot_questions.html',
        context={
            'questions': page.object_list, 'page_obj': page,
            'popular_tags': Tag.objects.get_popular_tags(), 'authorized': True}
    )


def question(request, question_id):
    if question_id > len(QUESTIONS) or question_id < 0:
        return HttpResponseNotFound("Question was not found")

    question = Question.objects.get(id=question_id)

    page = paginate(ANSWERS, request)

    return render(
        request, 'question.html',
        context={'question': question, 'popular_tags': Tag.objects.get_popular_tags(), 'answers': page.object_list,
                 'page_obj': page, 'authorized': True}
    )


def tag(request, tag_name):
    tag = Tag.objects.get(tag_name=tag_name)
    page = paginate(tag.question_set.all(), request)

    if page is None:
        return HttpResponseNotFound("Page was not found")

    tag = None
    for con_tag in TAGS:
        if con_tag.tag_name == tag_name:
            tag = con_tag

    if tag is None:
        return HttpResponseNotFound("Tag was not found")

    return render(
        request, 'tag_search.html',
        context={
            'popular_tags': Tag.objects.get_popular_tags(), 'tag': tag,
            'questions': page.object_list, 'page_obj': page, 'authorized': True
        }
    )


def ask(request):
    return render(
        request, 'ask.html',
        context={
            'popular_tags': Tag.objects.get_popular_tags(),
            'authorized': False,
        }
    )

def login(request):

    return render(
        request, 'login.html',
        context={'popular_tags': Tag.objects.get_popular_tags()}
    )


def signup(request):

    return render(
        request, 'signup.html',
        context={'popular_tags': Tag.objects.get_popular_tags()}
    )

def settings(request):
    return render(
        request, 'settings.html',
        context={'popular_tags': Tag.objects.get_popular_tags()}
    )
