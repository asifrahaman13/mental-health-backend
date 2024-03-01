# MENTAL HEALTH BOT

## How to run the code

First clone the repository:

```
git clone https://github.com/asifrahaman13/mental-health-backend
```

Next enter into the backend directory.

```
cd backend/
```

Create a virtual environment.

```
poetry shell
```

Activate the virtual environment. In unix based system like the Linux or Mac OS you can follow the following commands:

```
source .venv/bin/activate
```

Now install the required dependencies.

```
poetry install
```

Next enter the data into the .env and the .config files.

Now run the backend server.

```
poetry run uvicorn src.main:app --reload
```

<br/>
<br/>
<br/>
