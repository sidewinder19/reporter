# coding: utf-8
from datetime import date, timedelta

from .models import fetch_employee_salaries, fetch_dept_employees


class DepartmentSalariesReport():
    def __init__(self, session, from_inclusive, to_exclusive):
        self.session = session
        self.from_incl = from_inclusive
        self.to_excl = to_exclusive
         
    def report_department_salaries(self):
        dept_totals = dict()

        # Get a map of employees to salaries for the range.
        map_emp_to_salaries = self.build_map_emp_to_salaries()
    
        # Get a map of dept to dept / employee assocs during range.
        map_dept_to_dept_emps = self.build_map_dept_to_dept_employees()

        # Extract and sum up salaries for each dept / employee.
        for dept, dept_emps in map_dept_to_dept_emps.items():
            for de in dept_emps:
                emp_salaries = map_emp_to_salaries.get(de.emp_no, [])
                emp_salary_total = self.compute_salary(
                    de.from_date, de.to_date, emp_salaries)
                dept_totals[de.dept_no] = (
                    dept_totals.get(de.dept_no, 0) + emp_salary_total
                )
        return dept_totals

    def build_map_emp_to_salaries(self):
        """Buildup a map of employees to their salary(ies) in range."""
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
        """Get department / employee assocs during range."""
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

