# foxtel-ct-fastRest
# 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

Project overview and set-up

Our API will be simple, it will have 3 endpoints:

    POST /track will receive user_id and description. It creates a new task and starts a timer for it.
    POST /stop will receive an id and stop the timer for that task.
    GET /times will receive a user_id and date (e.g. 2023-07-16) and will respond with a list of tasks and the time spent in each, in that day.

Our database will have a single table, tasks, with the following columns:

    id, an auto-generated integer ID for the task.
    description, a textual description of the task.
    user_id, the integer ID of the user.
    start_time, the time the task was started.
    end_time, the time the task was stopped.

First things first, create a virtual environment for your project:

python3 -m venv .venv

Then activate it (the command differs on Windows):

source .venv/bin/activate

Then let's create a file called requirements.txt, and put in all the libraries we need:

fastapi
uvicorn
sqlalchemy
databases[sqlite]
pydantic
python-dotenv

To install all of these, run:

pip install -r requirements.txt

How to define database tables using SQLAlchemy

SQLAlchemy is an ORM, which means that instead of sending SQL queries to the database and receiving rows of data back, we deal with Python classes and objects.

The first step is to define the tables of data that our application needs.

Write this code in database.py:

import databases
import sqlalchemy

# Define the URL for our SQLite database. This is a file path which makes
# the database in a file called data.db in the current directory.
DATABASE_URL = "sqlite:///data.db"

# MetaData is a container object that keeps together different features of a database being described.
metadata = sqlalchemy.MetaData()

task_table = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer),
    sqlalchemy.Column("start_time", sqlalchemy.DateTime),
    sqlalchemy.Column("end_time", sqlalchemy.DateTime)
)

# Create an engine that stores data in the local directory's data.db file. 
# "check_same_thread" is set to False as SQLite connections are not thread-safe by default. 
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create all tables stored in this metadata in the actual file.
metadata.create_all(engine)

# Initialize a database connection.
database = databases.Database(DATABASE_URL)

How to set up our FastAPI app

The start of every FastAPI always looks similar! We create the FastAPI object, and then we can start setting up the routes or endpoints.

When clients make requests to one of our endpoints, we trigger a Python function that can perform some actions and respond with some data. That response data is then sent to the client.

Let's set up our FastAPI app in main.py:

from fastapi import FastAPI

app = FastAPI()

That's the FastAPI set-up! Now we need to do two things:

    Connect to our database.
    Write our endpoint functions.

How to connect to our database using FastAPI lifespan events

We can configure a lifespan event in FastAPI apps, which is a function that can perform some set-up before the FastAPI app starts running, and some tear-down after the FastAPI app finishes running.

We will use it to connect to our database.

To write the lifespan event, we write an async context manager, which is an async function decorated with @asynccontextmanager. This function must include a yield statement.

Any code before the yield will run before the FastAPI app starts. During the yield, the FastAPI app runs. This can take seconds, or much longer--even days! The code after the yield is our tear-down code, which runs after the FastAPI app finishes running.

Write this code in the main.py file:

from contextlib import asynccontextmanager

from database import database
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

The Pydantic models we need for data validation

FastAPI uses Pydantic models to automatically handle request validation, serialization, and documentation.

When clients send us data, we will pass this data through a Pydantic model to ensure it contains what we need. So if we need clients to send us a user_id and the id of the task, then we can write a Pydantic model for that.

We will need four Pydantic models:

    NewTaskItem, for when clients want to create a task. It ensures clients send us user_id, an integer, and description, a textual description of the task.
    TaskItem, for when clients want to stop a task. It ensures clients send us id, an integer.
    TaskOut, for when we want to respond with a task representation. We will use this model to ensure that our response has the right content. It ensures the response contains id, an integer, description, a string, and time_spent, a float.

Write this code in a models.py file:

from pydantic import BaseModel


class NewTaskItem(BaseModel):
    user_id: int
    description: str


class TaskItem(BaseModel):
    id: int


class TaskOut(BaseModel):
    id: int
    description: str
    time_spent: float


But up to now it may not be very clear how these models are used. Let's get into that with our first endpoint!
Writing an endpoint to start tracking a task

Here's our first endpoint. We'll add some code to main.py.

There are some new imports, add those at the top of the file. The rest of the code goes at the bottom of the file.

from datetime import datetime

from models import NewTaskItem
from database import task_table

...

@app.post("/track", response_model=TaskItem)
async def track(task: NewTaskItem):
    data = {**task.model_dump(), "start_time": datetime.now()}
    query = task_table.insert().values(data)
    last_record_id = await database.execute(query)

    return {"id": last_record_id}

When clients want to create a task, they'll send a request to our /track endpoint. They need to include the data that the TaskItem expects in the JSON payload of the request.

Pydantic will take that data and give us a TaskItem object. We then turn it into a dictionary using .model_dump() so we can insert it into our database. To that dictionary, we add the start_time.

To create a query to insert data, we use task_table.insert().values(data).

The id column is an integer primary key, which means it is auto-generated by the database when we create a new row.

When we execute an insert query, we get back the ID of the row we just inserted. We send that to the client so they can use it to stop the task later on.
Writing an endpoint to stop tracking a task

Just like the /track endpoint, our /stop endpoint needs to accept some data from the client, so we include a parameter with a Pydantic model.

In this case, we need to accept TaskItem, which includes id. We can then use this information to stop the task by updating its end_time in the database.

Let's update our main.py to include this endpoint:

from models import TaskItem

...

@app.post("/stop", response_model=TaskItem)
async def stop(task: TaskItem):
    end_time = datetime.now()
    query = (
        task_table.update().where(task_table.c.id == task.id).values(end_time=end_time)
    )
    await database.execute(query)
    return task

When a client sends a request to stop a task, they will include the task's ID. Pydantic will ensure that the field is present and is an integer, then provide us with a TaskItem object.

We then create a datetime object for the current time, which we will use as the end_time for the task.

To update a row in the table, we use the update method, specifying the row we want to update using the where method, and then the data we want to update using the values method.
Writing an endpoint to get the times worked on a day

When the client wants to get the tasks worked on a specific day, they need to send a GET request to the /times endpoint, with user_id and date as query parameters.

We calculate the start and end times of the day the client is interested in and then use these times to filter the tasks from the database.

Here's an example of what this URL might look like: http://our-api-domain.com/times?user_id=42&date=2023-07-18.

In this example, the client is requesting the tasks for the user with ID 42 on July 18th, 2023.

For FastAPI to take the query parameters from the URL, we need to add parameters to our function that aren't a Pydantic model (only int and str are supported for query string arguments).

Here's the code:

from datetime import timedelta, time

from models import GetTimesItem, TaskOut

...

@app.get("/times", response_model=list[TaskOut])
async def get_times(user_id: int, date: str):
    # Using `int` and `str` parameters instead of Pydantic models
    # tells FastAPI we want to get these values from the query string.
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    start_of_day = datetime.combine(selected_date, time.min)
    end_of_day = datetime.combine(selected_date, time.max)

    query = task_table.select().where(
        (task_table.c.user_id == user_id)
        & (task_table.c.start_time <= end_of_day)
        & ((task_table.c.end_time >= start_of_day) | (task_table.c.end_time.is_(None)))
    )
    tasks = await database.fetch_all(query)

    result = []
    for task in tasks:
        end_time = task["end_time"]
        if task["end_time"] is None:
            end_time = datetime.now()

        actual_start = max(task["start_time"], start_of_day)
        actual_end = min(end_time, end_of_day)
        duration = actual_end - actual_start

        result.append({**task, "time_spent": duration.total_seconds()})

    return result

Here, start_of_day and end_of_day mark the beginning and end of the day the user wants the time tracking for. By using datetime.combine, we can combine a date and a time. The first argument, the date, is given by the user. The second argument, time.min or time.max is the minimum or maximum value a time can be (00:00:00 or 23:59:59 respectively).

The select query fetches tasks from the database where the user_id matches, the start_time is before the end of the day and either end_time is after the start of the day or is not set (indicating an ongoing task).

In the loop, for each task, if end_time is not set, it's assigned the current time as the task is still ongoing. We then find the actual start and end times by clamping the task's start and end times to the start and end of the day. We calculate the duration by subtracting actual_start from actual_end and append the task to the result list.

Finally, we return the result list, which is a list of dictionaries containing all the task data and time_spent for each task.

This is by far the most complicated function in our application!

How to get a deployed PostgreSQL database from ElephantSQL

ElephantSQL is a PostgreSQL database hosting service. We can use it to get a deployed database for free. Here's how to get a database up and running:

    Go to the ElephantSQL website and create an account.
    Once logged in, click on "Create new instance".
    Choose the free plan, which gives you 20MB storage (good enough for a small project or for learning).
    Give your instance a name and select a region close to where your users will be.
    Click on "Select plan" at the bottom to create your instance.
    Once created, click on the instance name in your dashboard to view its details.
    In the details view, you will find your URL (in the format postgresql://user:password@host:port/dbname). This is your database URL, which you can plug into your application to connect to this database.

How to connect to your deployed database securely

It's not a good idea to hardcode the database connection string directly into your code, as this can pose significant security risks. For example, if your code is shared publicly (e.g., on a GitHub repository), anyone who has access to your code would also have access to your database!

A safer practice is to use environment variables to store sensitive information. An environment variable is a value that's available to your application's environment, and it can be read by your application. This way, you can share your code without exposing any sensitive information, as the actual credentials will be stored safely in the environment, not in the code.

To manage environment variables, we'll use the python-dotenv module, which allows you to specify environment variables in a .env file. This can be particularly handy during development, as it allows you to replicate the environment variables that will be used in production.

Create a .env file in the root of your project, and add the database connection string as an environment variable in the .env file:

DATABASE_URL="postgresql://username:password@hostname/databasename"

Then, in your database.py file, use os.getenv to get the value of the DATABASE_URL environment variable. Make sure to import the os module at the top of the file:

import os
import sqlalchemy
import databases

DATABASE_URL = os.getenv("DATABASE_URL")

metadata = sqlalchemy.MetaData()

# Define your tables here...

# You don't need check_same_thread=False when using PostgreSQL.
engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)
database = databases.Database(DATABASE_URL)

Now, when your application runs, it will read the DATABASE_URL from the environment variables, either from the .env file in a development environment or directly from the system environment in a production environment.
Ensuring the .env file doesn't end up in GitHub either

Now that we've moved the database connection string out of our code, we need to make sure that our .env file doesn't end up being publicly available, as that would defeat the point!

We need to make sure that the .env file doesn't end up in GitHub, and the best way to do that is to never commit it or upload it.

A good way to prevent accidentally committing the .env file to GitHub is by creating another file called .gitignore, and inside it putting this text:

.env

This tells Git to never include a file called .env in any commits.

How to deploy your FastAPI app to Render.com

    Push Your Code to a Git Repository: Render uses Git repositories to fetch and build applications. Push your code to a repository on a service like GitHub.
    Create a New Web Service on Render: Go to the Render dashboard and click on the "+ New" button, then select "Web Service."
    Select Your Repository: You'll be asked to provide a repository where your FastAPI project is hosted. Choose your repository and branch.
    Configure Your Service: You will need to specify some settings for your application:

    Build Command: This is the command Render will run to install your dependencies. If you're using Pipenv, this will be pipenv install. If you're using poetry, this will be poetry install. If you're using requirements.txt, it will be pip install -r requirements.txt.
    Start Command: This is the command to start your FastAPI server. Typically, it's uvicorn main:app --host 0.0.0.0 --port 10000. Replace main:app with the location of your FastAPI app if it's not in main.py at the root of your repository.

    Advanced Settings: Our application requires environment variables, so let's add one with the name of DATABASE_URL and the value of our ElephantSQL connection string.
    Deploy: Click "Save & Deploy" to create your service. Render will pull your code, install your dependencies, and start your service. Your service logs will be displayed, helping you monitor the deployment process.

Your FastAPI application should now be up and running on Render! The URL of your application will be in the format <service-name>.onrender.com.
Conclusion

We've walked you through building a simple yet practical time-tracking API with FastAPI and SQLAlchemy. This application can track tasks, stop tasks, and retrieve the time spent on tasks for a user on a given day.

If you're looking to take your FastAPI knowledge to the next level, check out our comprehensive FastAPI 101 course.

In this course, we cover how to build a complete, complex FastAPI project using pydantic, sqlalchemy, and more. We'll even guide you through implementing email confirmation, file uploads, and other advanced features. Join us in FastAPI 101 to make the most of FastAPI's speed and simplicity while building robust, production-ready applications.


