from datetime import date
#from django.test import TestCase
from unittest import TestCase
import time

from .models import (
    get_session, 
    remove_database, 
    create_database,
    drop_tables, create_tables, 
    Department, Employee, Salary, DeptEmp)


DATE_EARLIEST = date(1995, 2, 1)
DATE_BEGIN_ASSOCS = date(1996, 4, 2)
DATE_MIDDLE = date(1997, 6, 22)
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
        self.session.add(self.s1)
        self.s2 = Salary(
            emp_no='2',
            salary='60000',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_MIDDLE,
        )
        self.session.add(self.s2)
        self.s3 = Salary(
            emp_no='2',
            salary='70000',
            from_date=DATE_MIDDLE,
            to_date=DATE_FOREVER,
        )
        self.session.add(self.s3)

        # Department to Employee mappings
        self.de1 = DeptEmp(
            emp_no='1',
            dept_no='1',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_FOREVER,
        )
        self.session.add(self.de1)
        self.de2 = DeptEmp(
            emp_no='2',
            dept_no='1',
            from_date=DATE_BEGIN_ASSOCS,
            to_date=DATE_MIDDLE,
        )
        self.session.add(self.de2)
        self.de3 = DeptEmp(
            emp_no='2',
            dept_no='2',
            from_date=DATE_MIDDLE,
            to_date=DATE_FOREVER,
        )
        self.session.add(self.de3)

        self.session.commit() 


class DeptEmpTests(DatabaseTests):

    def test_count_records(self):
        res = self.session.query(Department).all()
        self.assertEquals(2, len(res))

        res = self.session.query(Employee).all()
        self.assertEquals(2, len(res))

    def test_query_dept_emp_all(self):
        date_start = DATE_EARLIEST
        date_end = DATE_FOREVER

        res = self.session.query(DeptEmp).filter(
            DeptEmp.to_date > date_start
        ).filter(
            DeptEmp.from_date < date_end).all()
        self.assertEquals(3, len(res))

    def test_query_dept_emp_partial(self):
        date_start = DATE_EARLIEST
        date_end = DATE_MIDDLE

        res = self.session.query(DeptEmp).filter(
            DeptEmp.to_date > date_start
        ).filter(
            DeptEmp.from_date < date_end).all()
        self.assertEquals(2, len(res))

