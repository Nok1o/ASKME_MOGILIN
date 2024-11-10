import random
from django.core.management.base import BaseCommand, CommandError
from app.models import Question, Answer, LikeQuestion, LikeAnswer, Profile, AUser, Tag

DEFAULT_RATIO = 10
MAX_TAGS = 8


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

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
        if options['ratio'] > 0:
            try:
                ratio = int(options['ratio'])
                if ratio <= 0:
                    raise ValueError
            except ValueError:
                raise CommandError('Please enter a valid ratio.')

        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        len_arr = 5000
        users = []
        profiles = []
        c = 0

        # Step 1: Create profiles in bulk
        for i in range(num_users):
            profile = Profile(bio="I am an ordinary user")
            profiles.append(profile)

        Profile.objects.bulk_create(profiles)

        # Step 2: Link profiles to AUser instances one by one
        for i, profile in enumerate(Profile.objects.all()[:num_users]):
            user = AUser(profile=profile, username=f"User {i + 1}", email="email@email.email")
            user.save()

        # if len(users):
        #     AUser.objects.bulk_create(users)
        # users.clear()

        print("Users and profiles done")
        tags = []
        c = 0

        for i in range(num_tags):
            tag = Tag(tag_name = f"tag {i + 1}")
            if c < len_arr:
                tags.append(tag)
            else:
                Tag.objects.bulk_create(tags)
                tags.clear()
                c = 0
            c += 1
        if len(tags):
            Tag.objects.bulk_create(tags)
            tags.clear()

        print("Tags done")

        questions = []
        c = 0

        for i in range(num_questions):
            question = Question(title="Question №" + str(i + 1),
                                text="This is a text for the question №" + str(i + 1))


            question.author = random.choice(AUser.objects.all())
            if c < len_arr:
                questions.append(question)
            else:
                Question.objects.bulk_create(questions)
                questions.clear()
                print(i)
                c = 0
            c += 1
        if len(questions):
            Question.objects.bulk_create(questions)
            questions.clear()

        for i in range(num_questions):
            Question.objects.get(id=i + 1).tags.set(self.get_tags(random.randint(0, MAX_TAGS + 1)))

        print("Questions done")

        answers = []
        c = 0

        for i in range(num_answers):
            question = random.choice(Question.objects.all())
            question.num_answers += 1
            auth = random.choice(AUser.objects.all())
            if auth == question.author:
                auth = (auth.id + 1) % num_users
            answer = Answer(question_id=question, author=auth,
                                           text=f'text for answer id={i}', is_correct=random.choice([True, False]))
            if c < len_arr:
                answers.append(answer)
            else:
                Answer.objects.bulk_create(answers)
                answers.clear()
                c = 0
            c += 1
            question.save(update_fields=['num_answers'])
        if len(answers):
            Answer.objects.bulk_create(answers)
            answers.clear()

        print("Answers done")

        likes_questions = []
        likes_answers = []
        c1 = 0
        c2 = 0

        for i in range(num_likes):
            rand = random.choice(['question', 'answer'])

            if rand == 'question':
                question = random.choice(Question.objects.all())
                question.num_likes += 1
                user = random.choice(AUser.objects.all())
                if user == question.author:
                    user = (user.id + 1) % num_answers

                like = LikeQuestion(question_id=question, user_id=user)
                if c1 < len_arr:
                    likes_questions.append(like)
                else:
                    LikeQuestion.objects.bulk_create(likes_questions)
                    likes_questions.clear()
                question.save(update_fields=['num_likes'])
                c1 += 1

            else:
                answer = random.choice(Answer.objects.all())
                answer.num_likes += 1
                user = random.choice(AUser.objects.all())
                if user == answer.author:
                    user = (user.id + 1) % num_answers

                like = LikeAnswer(answer_id=answer, user_id=user)
                answer.save(update_fields=['num_likes'])
                if c2 < len_arr:
                    likes_answers.append(like)
                else:
                    LikeAnswer.objects.bulk_create(likes_answers)
                    likes_answers.clear()
                c2 += 1
        if len(likes_questions):
            LikeQuestion.objects.bulk_create(likes_questions)
            likes_questions.clear()
        if len(likes_answers):
            LikeAnswer.objects.bulk_create(likes_answers)
            likes_answers.clear()

        print("Likes done")
