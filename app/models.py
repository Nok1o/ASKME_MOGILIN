import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

DEFAULT_POPULAR_TAGS_NUM = 10


class TagManager(models.Manager):
    def get_popular_tags(self, num=DEFAULT_POPULAR_TAGS_NUM):
        return sorted(self.all(), key=lambda tag: tag.question_set.all().count(), reverse=True)[:num]

    @staticmethod
    def get_questions(tag):
        return tag.question_set.all()


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)

    objects = TagManager()

    def __str__(self):
        return self.tag_name


class Profile(models.Model):
    image = models.ImageField(upload_to='user_uploads/', null=True, blank=True)
    bio = models.TextField(default='No Bio')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, default='user')


class QuestionManager(models.Manager):
    def get_best_questions(self):
        return self.all().order_by('-num_likes')

    def get_new_questions(self):
        return self.all().order_by('-date_posted')


    def get_amount_likes(self):
        return LikeQuestion.objects.filter(question_id=self.id).count()


class Question(models.Model):
    title = models.CharField()
    text = models.TextField(default='No Text')
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    num_likes = models.IntegerField(default=0)
    num_answers = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True)


    objects = QuestionManager()

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    def get_answers_for_question(self, question):
        return self.all().filter(question_id=question).order_by('-date_posted')

    def get_amount_likes(self):
        return LikeAnswer.objects.filter(answer_id=self.id).count()


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    num_likes = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True)

    objects = AnswerManager()

    def __str__(self):
        return "answer by " + self.author.__str__()


class LikeQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    unique_together = [question, user]

    def __str__(self):
        return 'like for question ' + self.question_id.__str__() + ' by ' + self.user_id.__str__()


class DislikeQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    unique_together = [question, user]

    def __str__(self):
        return 'like for question ' + self.question_id.__str__() + ' by ' + self.user_id.__str__()


class LikeAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    unique_together = [answer, user]

    def __str__(self):
        return 'like for answer' + self.answer_id.__str__() + 'by ' + self.user_id.__str__()


class DislikeAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    unique_together = [answer, user]

    def __str__(self):
        return 'like for answer' + self.answer_id.__str__() + 'by ' + self.user_id.__str__()