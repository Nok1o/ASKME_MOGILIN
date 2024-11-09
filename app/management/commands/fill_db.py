import random
from django.core.management.base import BaseCommand, CommandError
from app.models import Question, Answer, LikeQuestion, LikeAnswer, Profile, AUser, Tag

DEFAULT_RATIO = 10
MAX_TAGS = 5


class Command(BaseCommand):
    def get_tags(self, num_tags):
        tags = []
        if num_tags >= Tag.objects.count():
            tags = Tag.objects.all()
        else:
            for i in range(num_tags):
                while (tag := random.choice(Tag.objects.all())) in tags:
                    pass
                tags.append(tag)

        return tags

    def handle(self, *args, **options):
        ratio = DEFAULT_RATIO
        if len(args) > 0:
            try:
                ratio = int(args[0])
                if ratio <= 0:
                    raise ValueError
            except ValueError:
                raise CommandError('Please enter a valid ratio.')

        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        for i in range(num_users):
            profile = Profile.objects.create(bio="I am an ordinary user")
            user = AUser.objects.create_user(profile=profile, username=f"User {i + 1}", email="email@email.email")
            user.save()
            profile.save()

        for i in range(num_tags):
            tag = Tag.objects.create(tag_name = f"tag {i + 1}")
            tag.save()

        for i in range(num_questions):
            tag_am = random.randint(0, MAX_TAGS + 1)
            tags = self.get_tags(tag_am)

            question = Question.objects.create(title="Question №" + str(i + 1),
                                               text="This is a text for the question №" + str(i + 1))
            question.tags.set(tags)

            question.author = random.choice(AUser.objects.all())
            question.save()

        for i in range(num_answers):
            question = random.choice(Question.objects.all())
            question.num_answers += 1
            auth = random.choice(AUser.objects.all())
            if auth == question.author:
                auth = (auth.id + 1) % num_users
            answer = Answer.objects.create(question_id=question, author=auth,
                                           text=f'text for answer id={i}', is_correct=random.choice([True, False]))
            answer.save()

        for i in range(num_likes):
            rand = random.choice(['question', 'answer'])

            if rand == 'question':
                question = random.choice(Question.objects.all())
                question.num_likes += 1
                user = random.choice(AUser.objects.all())
                if user == question.author:
                    user = (user.id + 1) % num_answers

                like = LikeQuestion.objects.create(question_id=question, user_id=user)
                like.save()
            else:
                answer = random.choice(Answer.objects.all())
                answer.num_likes += 1
                user = random.choice(AUser.objects.all())
                if user == answer.author:
                    user = (user.id + 1) % num_answers

                like = LikeAnswer.objects.create(answer_id=answer, user_id=user)
                like.save()
