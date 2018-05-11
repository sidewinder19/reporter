# coding: utf-8
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


DB = {
    'drivername': 'mysql',
    'host': '172.18.0.2',
    'port': '3306',
    'username': 'reportinator', #  os.environ['DBUNAME'],
    'password': 'userpw', #  os.environ['DBPASS'],
    'database': 'employees', #  os.environ['DBNAME']
}


ENGINE = create_engine(URL(**DB))
SESSION = sessionmaker(bind=ENGINE)

Base = declarative_base()
metadata = Base.metadata


def get_session():
    return SESSION()


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


class Title(Base):
    __tablename__ = 'titles'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    title = Column(String(50), primary_key=True, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date)

    employee = relationship('Employee')

