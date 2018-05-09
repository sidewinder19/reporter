# Generated by Django 2.0.5 on 2018-05-09 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('dept_no', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('dept_name', models.CharField(max_length=40, unique=True)),
            ],
            options={
                'db_table': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Employees',
            fields=[
                ('emp_no', models.IntegerField(primary_key=True, serialize=False)),
                ('birth_date', models.DateField()),
                ('first_name', models.CharField(max_length=14)),
                ('last_name', models.CharField(max_length=16)),
                ('gender', models.CharField(max_length=1)),
                ('hire_date', models.DateField()),
            ],
            options={
                'db_table': 'employees',
            },
        ),
        migrations.CreateModel(
            name='DeptEmp',
            fields=[
                ('emp_no', models.ForeignKey(db_column='emp_no', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='web.Employees')),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('dept_no', models.ForeignKey(db_column='dept_no', on_delete=django.db.models.deletion.DO_NOTHING, to='web.Departments')),
            ],
            options={
                'db_table': 'dept_emp',
            },
        ),
        migrations.CreateModel(
            name='DeptManager',
            fields=[
                ('emp_no', models.ForeignKey(db_column='emp_no', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='web.Employees')),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('dept_no', models.ForeignKey(db_column='dept_no', on_delete=django.db.models.deletion.DO_NOTHING, to='web.Departments')),
            ],
            options={
                'db_table': 'dept_manager',
            },
        ),
        migrations.CreateModel(
            name='Salaries',
            fields=[
                ('emp_no', models.ForeignKey(db_column='emp_no', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='web.Employees')),
                ('salary', models.IntegerField()),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
            ],
            options={
                'db_table': 'salaries',
            },
        ),
        migrations.CreateModel(
            name='Titles',
            fields=[
                ('emp_no', models.ForeignKey(db_column='emp_no', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='web.Employees')),
                ('title', models.CharField(max_length=50)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'titles',
            },
        ),
        migrations.AlterUniqueTogether(
            name='titles',
            unique_together={('emp_no', 'title', 'from_date')},
        ),
        migrations.AlterUniqueTogether(
            name='salaries',
            unique_together={('emp_no', 'from_date')},
        ),
        migrations.AlterUniqueTogether(
            name='deptmanager',
            unique_together={('emp_no', 'dept_no')},
        ),
        migrations.AlterUniqueTogether(
            name='deptemp',
            unique_together={('emp_no', 'dept_no')},
        ),
    ]