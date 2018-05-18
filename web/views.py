from django.shortcuts import render
from django.http import HttpResponse

from .models import get_session
from .reports import build_report_dept_salaries, DepartmentSalariesReport

def index(request):
    session = get_session()    

    quarters, map_dept_to_salaries = build_report_dept_salaries(session)

    context = {
        'quarters': quarters,
        'map_dept_to_salaries': map_dept_to_salaries,
    }

    session.close()

    return render(request, 'web/deptsalaries.html', context)

