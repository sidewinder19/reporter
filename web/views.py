from datetime import date

from django.shortcuts import render
from django.http import HttpResponse

from .models import get_session
from .reports import build_report_dept_salaries, DepartmentSalariesReport

def index(request):
    """Generate and display salaries per deparments, for the requested date/range."""
    session = get_session()    

    # Set the start date to 0 (to auto-pick first year in database),
    # or else a provided start year.
    date_start = None
    year = int(request.GET.get('year', 0))
    if year > 1980:
        date_start = date(year, 1, 1)

    # Set the # quarters to report (default = 1 quarter).
    num_quarters = int(request.GET.get('quarters', 1))
    num_quarters = min(10 * 4, num_quarters)   

    # Build the report.
    quarters, map_dept_to_salaries = build_report_dept_salaries(
        session, 
        date_start_desired=date_start, num_quarters_desired=num_quarters)

    # Request is done with the connection.
    session.close()

    # Display salaries in a tabular format. 
    context = {
        'quarters': quarters,
        'map_dept_to_salaries': map_dept_to_salaries,
    }
    return render(request, 'web/deptsalaries.html', context)

