import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

DEFAULT_POPULAR_TAGS_NUM = 5


class TagManager(models.Manager):

    def get_popular_tags(self, num=DEFAULT_POPULAR_TAGS_NUM):
        res = sorted(self.all(), key=lambda tag: len(tag.question_set.all()), reverse=True)[:num]


        return sorted(self.all(), key=lambda tag: len(tag.question_set.all()), reverse=True)[:num]
class Tag(models.Model):
    tag_name = models.CharField(max_length=50)

    objects = TagManager()

    def __str__(self):
        return self.tag_name


class Profile(models.Model):
    image = models.ImageField(upload_to='profile_pics')
    bio = models.TextField(default='No Bio')
    #user = models.OneToOneField(User, on_delete=models.CASCADE)


class AUser(User):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)



class QuestionManager(models.Manager):
    def get_best_questions(self):
        return self.all().order_by('-num_likes').values()

    def get_new_questions(self):
        return self.all().order_by('-date_posted').values()


class Question(models.Model):
    title = models.CharField()
    text = models.TextField(default='No Text')
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    num_likes = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True)


    objects = QuestionManager()

    def __str__(self):
        return self.title


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField()
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    num_likes = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "answer by " + self.author.__str__()


class LikeQuestion(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    unique_together = [question_id, user_id]

    def __str__(self):
        return 'like for question ' + self.question_id.__str__() + ' by ' + self.user_id.__str__()


class LikeAnswer(models.Model):
    answer_id = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    unique_together = [answer_id, user_id]

    def __str__(self):
        return 'like for answer' + self.answer_id.__str__() + 'by ' + self.user_id.__str__()
