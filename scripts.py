import random

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from datacenter.models import (
    Chastisement,
    Commendation,
    Lesson,
    Mark,
    Schoolkid
)


def get_schoolkid(schoolkid_name):
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
        return schoolkid
    except MultipleObjectsReturned:
        print(
            f"Найдено несколько учеников с именем {schoolkid_name} - "
            f"уточните запрос добавив фамилию или отчество."
        )
        exit(1)
    except ObjectDoesNotExist:
        print(
            f"Ученик с именем {schoolkid_name}"
            f"не найден - проверьте корректность ввода."
        )
        exit(1)


def fix_marks(schoolkid_name):
    schoolkid = get_schoolkid(schoolkid_name)
    bad_marks = Mark.objects.filter(
        schoolkid=schoolkid,
        points__in=[2, 3]
    )
    return bad_marks.update(points=5) 


def remove_chastisements(schoolkid_name):
    schoolkid = get_schoolkid(schoolkid_name)
    return Chastisement.objects.filter(schoolkid=schoolkid).delete()


def get_lesson(schoolkid, subject_title, mode="latest"):
    order_by_map = {"latest": "-date", "first": "date", "random": "?"}
    if mode not in order_by_map:
        print(
            f"Неверный режим выбора урока: {mode}, "
            f"допустимые значения: latest, first, random"
        )
        exit(1)

    lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=subject_title,
    )
    lesson = lessons.order_by(order_by_map[mode]).first()

    if lesson is None:
        print(f"Урок по предмету `{subject_title}` без похвалы не найден.")
        exit(1)

    return lesson


def get_random_commendation_text():
    commendations = [
        "Отлично!",
        "Молодец!",
        "Замечательно!",
        "Прекрасная работа!",
        "Великолепно!",
        "Так держать!",
        "Браво!",
        "Супер!",
        "Ты на верном пути!",
        "Продолжай в том же духе!",
        "Заслуженно!",
        "Невероятно!",
        "Это потрясающе!",
        "Ты меня поразил!",
        "С каждым разом лучше!",
        "Я горжусь тобой!",
        "Ты справился на отлично!",
        "Идеально!",
        "Ты звезда!",
        "Ты супер-ученик!",
        "Лучший результат!",
        "Ты лидер!",
        "Ты превзошел себя!",
        "Впечатляет!",
        "Ты великолепен!",
    ]
    return random.choice(commendations)


def create_commendation(schoolkid_name, subject_title):
    schoolkid = get_schoolkid(schoolkid_name)
    lesson = get_lesson(schoolkid, subject_title)
    return Commendation.objects.create(
        text=get_random_commendation_text(),
        schoolkid=schoolkid,
        created=lesson.date,
        subject=lesson.subject,
        teacher=lesson.teacher,
    )
