from datetime import date
#from django.test import TestCase
from unittest import TestCase
import time

from .models import (
    get_session, 
    remove_database, 
    create_database,
    drop_tables, create_tables, 
    fetch_employee_salaries, fetch_dept_employees,
    Department, Employee, Salary, DeptEmp)

from .reports import DepartmentSalariesReport


DATE_EARLIEST = date(1995, 2, 1)
DATE_BEGIN_ASSOCS = date(1996, 4, 2)
DATE_MIDDLE = date(1997, 6, 22)
DATE_MIDDLE_PLUS = date(1998, 5, 6)
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


class DeptEmpTests(DatabaseTests):

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
        diff = set(expected) - set(res_repr)
        self.assertEquals(0, len(diff))
        diff = set(res_repr) - set(expected)
        self.assertEquals(0, len(diff))

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
        diff = set(expected) - set(res_repr)
        self.assertEquals(0, len(diff))
        diff = set(res_repr) - set(expected)
        self.assertEquals(0, len(diff))


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
        diff = set(expected) - set(res_repr)
        self.assertEquals(0, len(diff))
        diff = set(res_repr) - set(expected)
        self.assertEquals(0, len(diff))

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
        diff = set(expected) - set(res_repr)
        self.assertEquals(0, len(diff))
        diff = set(res_repr) - set(expected)
        self.assertEquals(0, len(diff))


class DepartmentSalariesReportTests(DatabaseTests):

    def test_compute_salary(self):
        days_total = (DATE_LAST_ASSOCS - DATE_BEGIN_ASSOCS).days
        salary_e1 = 50000.0 * days_total / 365

        days_e2_first = (DATE_MIDDLE_PLUS - DATE_BEGIN_ASSOCS).days 
        salary_e2_first = 60000.0 * days_e2_first / 365

        days_e2_second = (DATE_LAST_ASSOCS - DATE_MIDDLE_PLUS).days
        salary_e2_second = 70000.0 * days_e2_second / 365
 
        salary_total = int(salary_e1 + salary_e2_first + salary_e2_second)

        report = DepartmentSalariesReport(None, None, None)

        salaries = fetch_employee_salaries(
            self.session,
            DATE_EARLIEST,
            DATE_FOREVER,
        )

        test_total = report.compute_salary(
            DATE_EARLIEST,
            DATE_LAST_ASSOCS,
            salaries,
        )
        self.assertEquals(salary_total, test_total)

