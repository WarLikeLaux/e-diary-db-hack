import random

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from datacenter.models import (
    Chastisement,
    Commendation,
    Lesson,
    Mark,
    Schoolkid
)

class NoLessonException(Exception):
    pass


def get_schoolkid(schoolkid_name):
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
        return schoolkid
    except MultipleObjectsReturned:
        return (
            f"Найдено несколько учеников с именем {schoolkid_name} - "
            f"уточните запрос добавив фамилию или отчество."
        )
    except ObjectDoesNotExist:
        return (
            f"Ученик с именем {schoolkid_name}"
            f" не найден - проверьте корректность ввода."
        )


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
        return (
            f"Неверный режим выбора урока: {mode}, "
            f"допустимые значения: latest, first, random"
        )

    lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=subject_title,
    )
    commendations = Commendation.objects.filter(
        schoolkid=schoolkid,
        subject__title=subject_title
    )
    lessons_without_commendation = lessons.exclude(
        date__in=commendations.values_list('created', flat=True)
    )
    lesson = lessons_without_commendation.order_by(order_by_map[mode]).first()

    if lesson is None:
        raise NoLessonException(f"Урок по предмету `{subject_title}` без похвалы не найден.")

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


def format_commendation(commendation):
    return (
        f"Commendation: {commendation.text}"
        f", Schoolkid: {commendation.schoolkid.full_name}"
        f", Date: {commendation.created}"
        f", Subject: {commendation.subject.title}"
        f", Teacher: {commendation.teacher.full_name}"
    )


def create_commendation(schoolkid_name, subject_title):
    schoolkid = get_schoolkid(schoolkid_name)
    try:
        lesson = get_lesson(schoolkid, subject_title)
    except NoLessonException as error:
        return error
    created_commendation = Commendation.objects.create(
        text=get_random_commendation_text(),
        schoolkid=schoolkid,
        created=lesson.date,
        subject=lesson.subject,
        teacher=lesson.teacher,
    )
    return format_commendation(created_commendation)
