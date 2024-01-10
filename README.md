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

