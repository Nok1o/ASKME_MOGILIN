import copy
import random

from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.

QUESTIONS = [
    {
        "title": "Title " + str(i),
        "id": i,
        "text": "This is text for question №" + str(i),
        "likes": i,
        "tags": ['Tag_1', 'Tag_2', 'Tag_3', 'Tag_4'],
        "num_answers": i,
    }
    for i in range(1, 31)
]

ANSWERS = [
    {
        "text": "This is answer №" + str(i),
        "likes": i,
        "correct": i % 2 == 0
    }
    for i in range(1, 20)
]

TAGS = [
    {
        "tag": "Tag_" + str(i),
    }
    for i in range(1, 10)
]

AMOUNT_POPULAR_TO_SHOW = 5


def index(request):
    page = paginate(QUESTIONS, request)

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'index.html',
        context={
            'questions': page.object_list, 'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW],
            'page_obj': page, 'authorized': True
        }
    )


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


def hot_questions(request):
    hot_qs = copy.deepcopy(QUESTIONS)
    hot_qs.reverse()

    page = paginate(hot_qs, request)

    if page is None:
        return HttpResponseNotFound("Page was not found")

    return render(
        request, 'hot_questions.html',
        context={'questions': page.object_list, 'page_obj': page, 'tags': TAGS[-AMOUNT_POPULAR_TO_SHOW:], 'authorized': True}
    )


def question(request, question_id):
    if question_id > len(QUESTIONS) or question_id < 0:
        return HttpResponseNotFound("Question was not found")


    question = QUESTIONS[question_id - 1]

    page = paginate(ANSWERS, request)

    return render(
        request, 'question.html',
        context={'question': question, 'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW], 'answers': page.object_list,
                 'page_obj': page, 'authorized': True}
    )


def tag(request, tag_name):
    questions_tag = copy.deepcopy(QUESTIONS)
    random.shuffle(questions_tag)
    page = paginate(questions_tag, request)

    if page is None:
        return HttpResponseNotFound("Page was not found")

    tag = None
    for con_tag in TAGS:
        if con_tag['tag'] == tag_name:
            tag = con_tag

    if tag is None:
        return HttpResponseNotFound("Tag was not found")

    return render(
        request, 'tag_search.html',
        context={
            'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW], 'tag': tag,
            'questions': page.object_list, 'page_obj': page, 'authorized': True
        }
    )


def ask(request):
    return render(
        request, 'ask.html',
        context={
            'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW],
            'authorized': False,
        }
    )

def login(request):

    return render(
        request, 'login.html',
        context={'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW]}
    )


def signup(request):

    return render(
        request, 'signup.html',
        context={'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW]}
    )

def settings(request):
    return render(
        request, 'settings.html',
        context={'tags': TAGS[:AMOUNT_POPULAR_TO_SHOW]}
    )