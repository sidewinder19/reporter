# coding: utf-8
from datetime import date, timedelta

from .models import (
    fetch_departments,
    fetch_employee_salaries, 
    fetch_dept_employees,
    range_date_dept_emp,
)



def build_report_dept_salaries(
    session, date_start_desired=None, num_quarters_desired=4):
    """Top level report generation function.

    This function determmines what year to start the report at, and 
    for how many quarters thereafter. Then it calls the 
    DepartmentSalariesReport class to generate each quarter's department
    to total salary spend report. Each quarterly report is stitched into
    the final matrix of salaries per department over quarter.
    """

    # If not specified, pick the earliest date in the data set.
    date_start = date_start_desired
    if not date_start_desired:
        from_incl, _ = range_date_dept_emp(session)
        date_start = from_incl

    # Hard limit the number of quarters.
    num_quarters = min(12, num_quarters_desired)

    quarters = list()
    map_dept_to_salaries = dict()

    # Get departments.
    depts = [d.dept_name for d in fetch_departments(session)]
    if len(depts) <= 0:
        raise ValueError('No departments found')

    # Determine earliest quarter start date.
    start_incl = first_this_quarter(date_start)

    # Determine last date for report.
    num_years = int(num_quarters / 4)
    num_months = num_quarters * 3 - num_years * 12
    month_end = num_months + start_incl.month
    if month_end > 12:
        num_years += 1
        month_end -= 12
    end_excl = date(
        start_incl.year + num_years, month_end, start_incl.day)

    # Build quarterly report up.
    reporter = DepartmentSalariesReport(session, None, None) 
    next_start = start_incl
    while next_start < end_excl:
        next_end = first_next_quarter(next_start)
 
        quarters.append(quarter_name(next_start))
        
        map_dept_to_salary_total = reporter.report_department_salaries(
            from_in=next_start, to_ex=next_end) 
        for dept in depts:
            salaries = map_dept_to_salaries.get(dept, list())
            salary_total = map_dept_to_salary_total.get(dept, 0.0)
            salaries.append(salary_total)
            map_dept_to_salaries[dept] = salaries

        session.commit()

        next_start = next_end

    return quarters, map_dept_to_salaries


def first_this_quarter(date_now):
    """Get start of the current quarter for the specified date.

    The following table shows how the input date's month is mapped to
    the current quarter's month:
       date_now's month:          next quarter month:
            [1, 2, 3]                    1
            [4, 5, 6]                    4
            [7, 8, 9]                    7
            [10, 11, 12]                 10
    """
    month = date_now.month
    if month in [1, 2, 3]:
        month = 1
    elif month in [4, 5, 6]:
        month = 4
    elif month in [7, 8, 9]:
        month = 7
    else:
        month = 10
    return date(year=date_now.year, month=month, day=1)


def first_next_quarter(date_now):
    """Get start of the next quarter after the specified date.

    The following table shows how the input date's month is mapped to
    the following quarter's month:
       date_now's month:          next quarter month:
            [1, 2, 3]                    4
            [4, 5, 6]                    7
            [7, 8, 9]                    10
            [10, 11, 12]                 1 (following year)
    """
    month = date_now.month
    if month in [10, 11, 12]:
        return date(year=date_now.year + 1, month=1, day=1)

    if month in [4, 5, 6]:
        month = 7
    elif month in [7, 8, 9]:
        month = 10
    else:
        month = 4
    return date(year=date_now.year, month=month, day=1) 


def quarter_name(date_now):
    """Create a friendly name for the quarter the date_now is in."""
    quarter = 4
    month = date_now.month
    if month in [1, 2, 3]:
        quarter = 1
    elif month in [4, 5, 6]:
        quarter = 2
    elif month in [7, 8, 9]:
        quarter = 3
    return '{year} Q{quarter}'.format(
        year=date_now.year, quarter=quarter)


class DepartmentSalariesReport():
    """This class generates a report for the specified date range.

    The generated report shows total salary consumed per department,
    by employees assigned to the departent.

    The DeptEmp entities provide the date range that employees were
    assigned to the department. The Salary entities provide the date
    range that employees earned a specific annual salary for. This 
    class determines what portions of those employee salaries overlap
    with their tenure in a given department. Note that employees are
    assumed to consume a daily salary based on (annual salary / 365).
    This daily rate is then used to determine the final salary impact
    on their assigned department. This will not align with actual 
    payment dates to employees, so the results should be considered to 
    be an approximation of actual salaries consumed in a given quarter.

    This class uses a 'brute force' implementation, that could be 
    optimized. Please refer to the README.md documentation in the
    source repository for more information.
    """
    def __init__(self, session, from_inclusive, to_exclusive):
        self.session = session
        self.from_incl = from_inclusive
        self.to_excl = to_exclusive
         
    def report_department_salaries(self, from_in=None, to_ex=None):
        """Main method, computing department to total salary."""
        dept_totals = dict()

        # Allow overrides.
        if from_in:
            self.from_incl = from_in
        if to_ex:
            self.to_excl = to_ex

        # Build a map of department numbers to names.
        map_dept_no_to_name = {
           d.dept_no: d.dept_name for d in fetch_departments(self.session)
        }

        # Get a map of employees to salaries for the range.
        map_emp_to_salaries = self.build_map_emp_to_salaries()
    
        # Get a map of dept to dept / employee assocs during range.
        map_dept_no_to_dept_emps = self.build_map_dept_to_dept_employees()

        # Extract and sum up salaries for each dept / employee.
        for dept_no, dept_emps in map_dept_no_to_dept_emps.items():
            for de in dept_emps:
                emp_salaries = map_emp_to_salaries.get(de.emp_no, [])
                emp_salary_total = self.compute_salary(
                    de.from_date, de.to_date, emp_salaries)
                dept_name = map_dept_no_to_name.get(dept_no, '???')
                dept_totals[dept_name] = (
                    dept_totals.get(dept_name, 0) + emp_salary_total
                )
        return dept_totals

    def build_map_emp_to_salaries(self):
        """Build a map of employees to their salary(ies) in range."""
        map_e2s = dict()
        salaries_all = fetch_employee_salaries(
            self.session, self.from_incl, self.to_excl
        )
        for salary in salaries_all:
            try:
                map_e2s[salary.emp_no].append(salary)
            except KeyError:
                map_e2s[salary.emp_no] = [salary] 
        return map_e2s

    def build_map_dept_to_dept_employees(self):
        """Build a map of department / employee assocs in range."""
        map_d2de = dict()
        dept_emps_all = fetch_dept_employees(
            self.session, self.from_incl, self.to_excl
        )
        for dept_emp in dept_emps_all:
            try:
                map_d2de[dept_emp.dept_no].append(dept_emp)
            except KeyError:
                map_d2de[dept_emp.dept_no] = [dept_emp]
        return map_d2de

    def compute_salary(self, from_incl_sub, to_excl_sub, emp_salaries):
        """Compute the total salaries for date range.

        All employee salaries provided within the provided date range
        are summed up to a total amount. The provided salaries are 
        typically on behalf of a single employee. There could be more
        than one event if an employee received a raise during the 
        provided date range.
        """ 

        salary_total = 0.0

        # Restrict range to this instance's configured range.
        from_in = from_incl_sub
        if from_incl_sub < self.from_incl:
            from_in = self.from_incl 
        elif from_incl_sub >= self.to_excl:
            return salary_total

        to_ex = to_excl_sub
        if to_excl_sub > self.to_excl:
            to_ex = self.to_excl
        elif to_excl_sub <= self.from_incl:
            return salary_total 

        # Compute total salaries.
        days_max = (to_ex - from_in).days
        for salary in emp_salaries:

            # If salary is at lower end of overall range.
            if salary.from_date <= from_in:
                days = (salary.to_date - from_in).days

            # If salary is at upper end of overall range.
            elif salary.to_date >= to_ex:
                days = (to_ex - salary.from_date).days

            # Else, salary range is nested in overall range.
            else:
                days = (salary.to_date - salary.from_date).days

            # Compute salary consumed during overall range.
            days = min(days, days_max)
            days = max(days, 0)
            salary_next = float(salary.salary) * days / 365
            salary_total += salary_next

        return salary_total

