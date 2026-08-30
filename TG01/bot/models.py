from django.db import models


class Student(models.Model):
    user_id = models.BigIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, null = True, blank = True)
    age = models.IntegerField()
    grade = models.CharField(max_length=100, null = True, blank = True)

    def __str__(self):
        return f"{self.name} | {self.user_id}"