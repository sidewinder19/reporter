from datetime import date
from django.test import TestCase

from .models import (get_session, Department)


DATE_EARLIEST = date(1995, 2, 1)
DATE_BEGIN_ASSOCS = date(1996, 4, 2)
DATE_MIDDLE = date(1997, 6, 22)
DATE_LAST_ASSOCS = date(1999, 10, 31)
DATE_LATEST = date(2000, 3, 6)
DATE_FOREVER = date(9999, 1, 1)


def seed_models(session):
    d1 = Department(dept_no='1', dept_name='old dept')
    d2 = Department(dept_no='2', dept_name='new dept')

    session.add(d1)
    session.add(d2)
    session.commit()

class DeptEmpTests(TestCase):

    def setUp(self):
        self.session = get_session()
        seed_models(self.session)

    def test(self):
        res = self.session.query(Department).all()
        self.assertEquals(2, len(res))

