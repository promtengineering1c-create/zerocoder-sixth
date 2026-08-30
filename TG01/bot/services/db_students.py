from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from bot.models import Student


@sync_to_async
def get_student_or_none(user_id: int):
    try:
        return Student.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return None

@sync_to_async
def save_student(user_id: int, name: str, age: int, grade: str):
    Student.objects.update_or_create(
        user_id=user_id,
        defaults={'name': name, 'age': age, 'grade': grade}
    )