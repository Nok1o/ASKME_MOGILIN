import os
import random
from django.core.management.base import BaseCommand, CommandError
from django.template.context_processors import static

from app.models import Question, Answer, LikeQuestion, LikeAnswer, Profile, User, Tag
from django.db import connection
from askme_mogilin import settings

DEFAULT_RATIO = 10000
MAX_TAGS = 8


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=DEFAULT_RATIO)


    def handle(self, *args, **options):
        ratio = options['ratio']
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        len_arr = 5000  # batch size

        # creating users
        users = [User(username=f"User {i + 1}", email="email{i}@domain.com") for i in range(num_users)]
        User.objects.bulk_create(users)
        user_objects = list(User.objects.all())

        pics = os.listdir(settings.BASE_DIR / 'static/img/profile_pics')
        profiles = [Profile(bio="I am an ordinary user", user=user, image=f'img/profile_pics/{random.choice(pics)}')
                    for _, user in enumerate(user_objects)]
        Profile.objects.bulk_create(profiles)
        print("Users and profiles done")

        # creating tags
        tags = [Tag(tag_name=f"tag {i + 1}") for i in range(num_tags)]
        Tag.objects.bulk_create(tags)
        tag_objects = list(Tag.objects.all())
        print("Tags done")

        # creating questions
        questions = [
            Question(title=f"Question №{i + 1}", text=f"This is a text for question №{i + 1}",
                     author=random.choice(user_objects))
            for i in range(num_questions)
        ]
        Question.objects.bulk_create(questions, batch_size=len_arr)
        question_objects = list(Question.objects.all())
        print("Questions done")

        # assigning tags to questions
        question_ids = [question.id for question in question_objects]
        tag_ids = [tag.id for tag in tag_objects]
        question_tag_pairs = []
        for question_id in question_ids:
            assigned_tags = random.sample(tag_ids, random.randint(0, MAX_TAGS))
            question_tag_pairs.extend((question_id, tag_id) for tag_id in assigned_tags)

        with connection.cursor() as cursor:
            cursor.executemany(
                'insert into app_question_tags (question_id, tag_id) values (%s, %s)',
                question_tag_pairs
            )

        print("Question tags assigned")

        # creating answers
        answers = []
        for i in range(num_answers):
            question = random.choice(question_objects)
            author = random.choice(user_objects)
            answers.append(
                Answer(question=question, author=author, text=f"This is an answer {i + 1}", is_correct=random.choice([True, False]))
            )
        Answer.objects.bulk_create(answers, batch_size=len_arr)

        print("Answers done")

        # creating likes
        likes_questions = []
        likes_answers = []
        for _ in range(num_likes):
            user = random.choice(user_objects)
            if random.choice(['question', 'answer']) == 'question':
                question = random.choice(question_objects)
                likes_questions.append(LikeQuestion(question=question, user=user))
            else:
                answer = random.choice(answers)
                likes_answers.append(LikeAnswer(answer=answer, user=user))

        LikeQuestion.objects.bulk_create(likes_questions, batch_size=len_arr)
        LikeAnswer.objects.bulk_create(likes_answers, batch_size=len_arr)

        print("Likes done")

        # updating num_likes and num_answers for questions, answers
        with connection.cursor() as cur:
            cur.execute('update app_question '
                        'set num_likes = coalesce(('
                        '    select count(*)'
                        '    from app_likequestion'
                        '    where app_likequestion.question_id = app_question.id),  0);')

            cur.execute('update app_answer '
                        'set num_likes = coalesce(('
                        '    select count(*)'
                        '    from app_likeanswer'
                        '    where app_likeanswer.answer_id = app_answer.id), 0);')

            cur.execute('update app_question '
                        'set num_answers = coalesce((select gr.cnt '
                        'from ('
                        '    select question_id, count(*) as cnt'
                        '    from app_answer'
                        '    group by question_id) gr '
                        'where gr.question_id = app_question.id), 0);')

            print("num_likes and num_answers updated")
