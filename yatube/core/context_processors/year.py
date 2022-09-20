import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now_year = datetime.date.today().year
    return {
        'year': now_year
    }
