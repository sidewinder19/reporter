from datetime import date

from django.shortcuts import render
from django.http import HttpResponse

from .models import get_session
from .reports import build_report_dept_salaries, DepartmentSalariesReport

def index(request):
    session = get_session()    

    date_start = None
    year = int(request.GET.get('year', 0))
    if year > 1980:
        date_start = date(year, 1, 1)

    num_quarters = int(request.GET.get('quarters', 1))
    num_quarters = min(10 * 4, num_quarters)   

    quarters, map_dept_to_salaries = build_report_dept_salaries(
        session, 
        date_start_desired=date_start, num_quarters_desired=num_quarters)

    context = {
        'quarters': quarters,
        'map_dept_to_salaries': map_dept_to_salaries,
    }

    session.close()

    return render(request, 'web/deptsalaries.html', context)

