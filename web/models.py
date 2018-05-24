# coding: utf-8
from sqlalchemy import (
    and_, asc, create_engine, desc, func, 
    Column, Date, ForeignKey, Integer, String, Table
)
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import UnboundExecutionError 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

import os


ENGINE = None
SESSION_FACTORY = None

Base = declarative_base()
metadata = Base.metadata


def get_configs(test_mode=False):
   """Retrieve database configs from environment"""
   conf = {
       'drivername': 'mysql',
       'host': os.environ['MYSQL_HOST'],  # Ex: '172.18.0.2'
       'port': os.environ['MYSQL_PORT'],  # Ex: '3306'
       'username': os.environ['MYSQL_USER'], # Ex: 'reportinator'
       'password': os.environ['MYSQL_PASSWORD'], # Ex: 'userpw'
       'database': 'employees',
   }
   if test_mode:
       conf['host'] = os.environ['MYSQL_HOST_TEST']
       conf['port'] = os.environ['MYSQL_PORT_TEST']
       conf['database'] = 'test_' + conf['database']
   return conf


def get_engine(test_mode=False):
    """Create our database engine."""
    global ENGINE
    if ENGINE:
        return ENGINE

    conf = get_configs(test_mode=test_mode)
    ENGINE = create_engine(URL(**conf))
    return ENGINE


def create_tables(test_mode=False):
    """Create database tables based on models below."""
    engine = get_engine(test_mode=test_mode)    
    metadata.create_all(bind=engine)


def get_session_factory(test_mode=False):
    """Create our factory to create database connections."""
    global SESSION_FACTORY
    if SESSION_FACTORY:
        return SESSION_FACTORY

    engine = get_engine(test_mode=test_mode)    

    SESSION_FACTORY = scoped_session(sessionmaker(bind=engine))

    return SESSION_FACTORY


def get_session(test_mode=False):
    """Get a session/connection to use with our database."""
    return get_session_factory(test_mode=test_mode)()


def drop_tables(test_mode=False):
    """Drop tables in the target database."""
    engine = get_engine(test_mode=test_mode)
    try:
        metadata.drop_all(engine)
    except UnboundExecutionError:
        pass  # Database doesn't exist yet, so noting to remove.


def fetch_departments(session):
    """Fetch departments."""
    depts = session.query(Department).all()
    return depts


def fetch_employee_salaries(session, from_incl, to_excl):
    """Get Salaries that start/end overlapping with provided range."""
    salaries = session.query(Salary).filter(
        and_(Salary.to_date > from_incl, Salary.from_date < to_excl)
    ).all()
    return salaries


def fetch_dept_employees(session, from_incl, to_excl):
    """Get DeptEmps that start/end overlapping with provided range."""
    dept_emps = session.query(DeptEmp).filter(
        and_(DeptEmp.to_date > from_incl, DeptEmp.from_date < to_excl)
    ).all()
    return dept_emps


def range_date_dept_emp(session):
    """Get date range of all possible DeptEmp entities."""
    de_first = session.query(DeptEmp).order_by(asc('from_date')).first()
    from_incl = de_first.from_date

    # Get last date in range.
    # NOTE: Do not query by the last to_date, as it can have an 
    # 'infite' date of 9999.
    de_last = session.query(DeptEmp).order_by(desc('from_date')).first()
    to_excl = de_last.from_date
 
    return from_incl, to_excl


# =======
# Generated models below. Avoid hand modifying these classes.
# =======


t_current_dept_emp = Table(
    'current_dept_emp', metadata,
    Column('emp_no', Integer),
    Column('dept_no', String(4)),
    Column('from_date', Date),
    Column('to_date', Date)
)


class Department(Base):
    __tablename__ = 'departments'

    dept_no = Column(String(4), primary_key=True)
    dept_name = Column(String(40), nullable=False, unique=True)


class DeptEmp(Base):
    __tablename__ = 'dept_emp'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    department = relationship('Department')
    employee = relationship('Employee')

    def __repr__(self):
        return (
            'DeptEmp(emp_no={}, dept_no={}, from={}, to={})'.format(
            self.emp_no, self.dept_no, self.from_date, self.to_date))


t_dept_emp_latest_date = Table(
    'dept_emp_latest_date', metadata,
    Column('emp_no', Integer),
    Column('from_date', Date),
    Column('to_date', Date)
)


class DeptManager(Base):
    __tablename__ = 'dept_manager'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    department = relationship('Department')
    employee = relationship('Employee')


class Employee(Base):
    __tablename__ = 'employees'

    emp_no = Column(Integer, primary_key=True)
    birth_date = Column(Date, nullable=False)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(ENUM('M', 'F'), nullable=False)
    hire_date = Column(Date, nullable=False)


class Salary(Base):
    __tablename__ = 'salaries'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    salary = Column(Integer, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date, nullable=False)

    employee = relationship('Employee')

    def __repr__(self):
        return (
            'Salary(emp_no={}, salary={}, from={}, to={})'.format(
            self.emp_no, self.salary, self.from_date, self.to_date))


class Title(Base):
    __tablename__ = 'titles'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    title = Column(String(50), primary_key=True, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date)

    employee = relationship('Employee')

