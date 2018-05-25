# Reporter System

The Reporter System is a proof of concept project to create a report showing quarterly spending by department, for the sample datagbase available [here](https://github.com/datacharmer/test_db)

## Caveats

WARNING! This POC uses a brute-force approach to gathering database data and then generating the report data, resulting in a report that can take very long to build for years further into the sample dataset installed below. 

Additionally, the POC doesn't try to build this report in the background, rather it computes the report on each web request made to display it. 

Finally, this POC is not deemed to be secure, with no secret environment variables or TLS certificates used to harden passwords and inter-container communications.

Steps that could be taken to move this POC into a more production ready status are detailed at the end of this read me file. 

## Getting Started

These instructions install a copy of the project on your local machine for development and testing purposes.

### Prerequisites

These directions are targeted for setup on an Ubuntu instance (tested with 16.04 on an EC2 instance). 

### Installing

On your target Ubuntu system, install `make` and `git` as follows:

```
sudo apt-get update && sudo apt-get install -y make git 
```

Then clone and change-directory to this repository, as follows:

```
git clone https://github.com/sidewinder19/reporter.git
cd reporter
```

Then configure the Docker and MySQL configuration files as follows:

```
cp sample-env .env
vi .env   (change passwords as you see fit)
chmod 600 .env

cp sample-.my.cnf ~/.my.cnf
vi ~/.my.cnf   (change master password, matching with .env above)
chmod 600 ~/.my.cnf
```

Next, run the 'all' make target, to install remaining dependencies, boot up the Docker containers, run tests and execute a sample curl call:

```
make all
```

## Running the tests

Once installed successfully per the previous section, tests can be run again by calling:

```
make tests
```

These tests check the database ORM models and access functions, used to interface with the MySQL database. They also test out the report generator used to compute quarterly salary spend per department.

## Running a request to generate a report

Reports are generated each time a request is made to the web node spun up via the `make all` target above, using a `curl` command such as this one:

```
curl -X GET http://172.18.0.4:8000/reports/?quarters=2
```

Where the IP address used is available via this call:

```
sudo docker inspect --format '{{ .NetworkSettings.Networks.reporter_backend.IPAddress }}' reporter_api_1
```

## Next Steps

This proof-of-concept project uses docker-compose to build and run containers on a local target Ubuntu machine. More work is needed before this project can be pushed into production, as detailed in the following sections.

### Report Generation Tied to Web Requeest

The department/salary report is only generated when requested from the web request in the 'Running a request...' section above. Generally speaking, reports can take a while to generate, and therefore should be run as periodic process *outside* of the actions from a Jenkins server would support automated CI/CD processes as well.
 web request. The web request should therefore be retrieving and displaying the *result* of this report generation.

### Optimizing report generation

The report generation used currently is a brute force approach, pulling DeptEmp and Salary entities that span each quarterly date range computed for the report. The sample data set however quickly adds thousands of DeptEmp and Salary entities that match this criteria. If a DeptEmp or Salary employee to date range spans multiple quarters (or lasts 'forever' as signified by a year of 9999), then it will be retrieved for all subsequent quarters, in addition to any new ranges added, so there is a compounding effect of even more entities retrieved and processed with subsequent quarters. 

Simply joining the Salary entities with DeptEmp ones is not sufficient, as date ranges for a given employee can change independently over time. They can also only consume one day of the entire quarter (so 1/365th of annual salary, or the entire quarter.

A more efficient approach would be to cache the DeptEmp and Salary entities that span across subsequent quarters, as they will always take up 3 months worth of salary impact with no need for special computation. Then, only new date ranges, or terminating ranges for cached entitites, for these two entity types have to be specially processed. The only downside is that the entire data set would need to be processed from the start, rather than selecting any year/quarter in the data set.

Hence next steps should be to pursue this more efficient entity caching approach, combined with generating and caching the report on a quarterly basis, for quick retrieval on GET requests thereafter. 

### Deployment to production

The docker-compose file provided and associated Dockerfiles only run on one Docker host currently. [This blog](https://medium.com/@basi/docker-compose-from-development-to-production-88000124a57c) provides an approach to create Docker images that can be run in staging or production, such as via AWS ECS. Executing these actions from a Jenkins server would support automated CI/CD processes. 

It would also be good to add an nginx reverse proxy server in front of the Django server, to support TLS, caching, etc. The SQLAlchemy session process also needs to be tied in with Django's request lifecycle, rather than explicitly invoked as done now.

## Authors

* **John Wood** - *Initial project setup* - [sidewinder19](https://github.com/sidewinder19)

