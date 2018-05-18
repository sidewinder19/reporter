from datetime import date
#from django.test import TestCase
from unittest import TestCase
import time

from .models import (
    get_session, 
    remove_database, 
    create_database,
    drop_tables, create_tables, 
    fetch_departments,
    fetch_employee_salaries, 
    fetch_dept_employees,
    range_date_dept_emp,
    Department, Employee, Salary, DeptEmp)

from .reports import (
    build_report_dept_salaries,
    build_report_dept_salaries,
    first_this_quarter,
    first_next_quarter,
    DepartmentSalariesReport)


DATE_EARLIEST = date(1995, 2, 1)
DATE_BEGIN_QUARTER = date(1996, 4, 1)
DATE_BEGIN_ASSOCS = date(1996, 4, 2)
DATE_MIDDLE = date(1997, 6, 22)
DATE_MIDDLE_PLUS = date(1998, 5, 6)
DATE_END_QUARTER = date(1998, 7, 1)
DATE_LAST_ASSOCS = date(1999, 10, 31)
DATE_LATEST = date(2000, 3, 6)
DATE_FOREVER = date(9999, 1, 1)


class DatabaseTests(TestCase):

    def setUp(self):
        print('setUp')
        drop_tables(test_mode=True)
        create_tables(test_mode=True)
        self.session = get_session(test_mode=True)
        self._seed_models()

    def tearDown(self):
        print('tearDown')
        self.session.commit()
        self.session.close()

    def _seed_models(self):
        # Departments
        self.d1 = Department(dept_no='1', dept_name='old dept')
        self.d2 = Department(dept_no='2', dept_name='new dept')
        self.session.add(self.d1)
        self.session.add(self.d2)

        # Employees
        self.e1 = Employee(
            emp_no='1', 
            birth_date=DATE_EARLIEST,
            first_name='Adam',
            last_name='First',
            gender='M',
            hire_date=DATE_BEGIN_ASSOCS,
        )
        self.session.add(self.e1)
        self.e2 = Employee(
            emp_no='2',
            birth_date=DATE_EARLIEST,
            first_name='Eve',
            last_name='Second',
            gender='F',
            hire_date=DATE_BEGIN_ASSOCS,
        )
        self.session.add(self.e2)

        # Salaries
        self.s1 = Salary(
            emp_no='1',
            salary='50000',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_FOREVER,
        )
        self.s1_repr = str(self.s1)
        self.session.add(self.s1)
        self.s2 = Salary(
            emp_no='2',
            salary='60000',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_MIDDLE_PLUS,
        )
        self.s2_repr = str(self.s2)
        self.session.add(self.s2)
        self.s3 = Salary(
            emp_no='2',
            salary='70000',
            from_date=DATE_MIDDLE_PLUS,
            to_date=DATE_FOREVER,
        )
        self.s3_repr = str(self.s3)
        self.session.add(self.s3)

        # Department to Employee mappings
        self.de1 = DeptEmp(
            emp_no='1',
            dept_no='1',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_FOREVER,
        )
        self.de1_repr = str(self.de1)
        self.session.add(self.de1)
        self.de2 = DeptEmp(
            emp_no='2',
            dept_no='1',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_MIDDLE,
        )
        self.de2_repr = str(self.de2)
        self.session.add(self.de2)
        self.de3 = DeptEmp(
            emp_no='2',
            dept_no='2',
            from_date=DATE_MIDDLE,
            to_date=DATE_FOREVER,
        )
        self.de3_repr = str(self.de3)
        self.session.add(self.de3)   

        self.session.commit() 

    def _assert_results_equal(self, expected, res_repr):
        diff = set(expected) - set(res_repr)
        self.assertEquals(0, len(diff))
        diff = set(res_repr) - set(expected)
        self.assertEquals(0, len(diff))


class DepartmentTests(DatabaseTests):

    def test_fetch(self):
        depts = fetch_departments(self.session)
        self.assertEquals(2, len(depts))


class DeptEmpTests(DatabaseTests):

    def test_range_date_dept_emp(self):
        from_incl, to_excl = range_date_dept_emp(self.session)
        self.assertEquals(DATE_BEGIN_ASSOCS, from_incl)
        self.assertEquals(DATE_MIDDLE, to_excl)

    def test_count_records(self):
        res = self.session.query(Department).all()
        self.assertEquals(2, len(res))

        res = self.session.query(Employee).all()
        self.assertEquals(2, len(res))

    def test_query_all(self):
        date_start = DATE_EARLIEST
        date_end = DATE_FOREVER

        res = fetch_dept_employees(
            self.session,
            date_start,
            date_end,
        )
        self.assertEquals(3, len(res))

        expected = [self.de1_repr, self.de2_repr, self.de3_repr] 
        res_repr = [str(r) for r in res]
        self._assert_results_equal(expected, res_repr)

    def test_query_partial(self):
        date_start = DATE_EARLIEST
        date_end = DATE_MIDDLE


        res = fetch_dept_employees(
            self.session,
            date_start,
            date_end,
        )
        self.assertEquals(2, len(res))

        expected = [self.de1_repr, self.de2_repr]
        res_repr = [str(r) for r in res]
        self._assert_results_equal(expected, res_repr)


class SalaryTests(DatabaseTests):

    def test_count_records(self):
        res = self.session.query(Salary).all()
        self.assertEquals(3, len(res))

    def test_query_all(self):
        date_start = DATE_EARLIEST
        date_end = DATE_FOREVER

        res = fetch_employee_salaries(
            self.session,
            date_start,
            date_end,
        )
        self.assertEquals(3, len(res))

        expected = [self.s1_repr, self.s2_repr, self.s3_repr]
        res_repr = [str(r) for r in res]
        self._assert_results_equal(expected, res_repr)

    def test_query_partial(self):
        date_start = DATE_EARLIEST
        date_end = DATE_MIDDLE

        res = fetch_employee_salaries(
            self.session,
            date_start,
            date_end,
        )
        self.assertEquals(2, len(res))

        expected = [self.s1_repr, self.s2_repr]
        res_repr = [str(r) for r in res]
        self._assert_results_equal(expected, res_repr)


class DepartmentSalariesReportTests(DatabaseTests):

    def setUp(self):
        super().setUp()
        self.report = DepartmentSalariesReport(
            self.session, 
            DATE_BEGIN_QUARTER, 
            DATE_END_QUARTER)

        self.days_total = (DATE_END_QUARTER - DATE_BEGIN_ASSOCS).days
        self.salary_e1 = 50000.0 * self.days_total / 365

        self.days_e2_first = (DATE_MIDDLE_PLUS - DATE_BEGIN_ASSOCS).days 
        self.salary_e2_first = 60000.0 * self.days_e2_first / 365

        self.days_e2_second = (DATE_END_QUARTER - DATE_MIDDLE_PLUS).days
        self.salary_e2_second = 70000.0 * self.days_e2_second / 365
 
        self.salary_total = (
            self.salary_e1 + self.salary_e2_first + self.salary_e2_second)

    def test_first_this_quarter(self):
        d = date(1999, 1, 25)
        r = first_this_quarter(d)
        self.assertEquals(date(1999, 1, 1), r)

        d = date(1999, 1, 1)
        r = first_this_quarter(d)
        self.assertEquals(date(1999, 1, 1), r)

        d = date(1999, 5, 2)
        r = first_this_quarter(d)
        self.assertEquals(date(1999, 4, 1), r)

        d = date(1999, 9, 12)
        r = first_this_quarter(d)
        self.assertEquals(date(1999, 7, 1), r)

        d = date(1999, 12, 31)
        r = first_this_quarter(d)
        self.assertEquals(date(1999, 10, 1), r)

    def test_first_next_quarter(self):
        d = date(1999, 1, 25)
        r = first_next_quarter(d)
        self.assertEquals(date(1999, 4, 1), r)

        d = date(1999, 1, 1)
        r = first_next_quarter(d)
        self.assertEquals(date(1999, 4, 1), r)

        d = date(1999, 5, 2)
        r = first_next_quarter(d)
        self.assertEquals(date(1999, 7, 1), r)

        d = date(1999, 9, 12)
        r = first_next_quarter(d)
        self.assertEquals(date(1999, 10, 1), r)

        d = date(1999, 12, 31)
        r = first_next_quarter(d)
        self.assertEquals(date(2000, 1, 1), r)

    def test_compute_salary(self):
        salaries = fetch_employee_salaries(
            self.session,
            DATE_EARLIEST,
            DATE_FOREVER,
        )

        test_total = self.report.compute_salary(
            DATE_EARLIEST,
            DATE_FOREVER,
            salaries,
        )
        self.assertEquals(self.salary_total, test_total)

    def test_build_map_emp_to_salaries(self):
        map_e2s = self.report.build_map_emp_to_salaries()
        self.assertEquals(2, len(map_e2s))
        
        e1s = map_e2s[1]
        self.assertEquals(1, len(e1s))
        expected = [self.s1_repr]
        res_repr = [str(r) for r in e1s]
        self._assert_results_equal(expected, res_repr)

        e2s = map_e2s[2]
        self.assertEquals(2, len(e2s))
        expected = [self.s2_repr, self.s3_repr]
        res_repr = [str(r) for r in e2s]
        self._assert_results_equal(expected, res_repr)

    def test_build_map_dept_to_dept_employees(self):
        map_d2des = self.report.build_map_dept_to_dept_employees()
        self.assertEquals(2, len(map_d2des))
        
        d1s = map_d2des['1']
        self.assertEquals(2, len(d1s))
        expected = [self.de1_repr, self.de2_repr]
        res_repr = [str(d) for d in d1s]
        self._assert_results_equal(expected, res_repr)

        d2s = map_d2des['2']
        self.assertEquals(1, len(d2s))
        expected = [self.de3_repr]
        res_repr = [str(d) for d in d2s]
        self._assert_results_equal(expected, res_repr)

    def test_integrated_one_report(self):
        dept_totals = self.report.report_department_salaries()
        self.assertEquals(2, len(dept_totals))

        test_total = dept_totals['old dept'] + dept_totals['new dept']
        self.assertEquals(self.salary_total, test_total)

    def test_integrated_quarterly_reports(self):
        quarters, map_d2s = build_report_dept_salaries(self.session)

        self.assertEquals(9, len(quarters))
        self.assertEquals(2, len(map_d2s))

        self.assertEquals('1996 Q2', quarters[0])

        total_salary = 0.0
        for dept, salaries in map_d2s.items():
            total_salary += sum(salaries)
        self.assertAlmostEquals(self.salary_total, total_salary)

