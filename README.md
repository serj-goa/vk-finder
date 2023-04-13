# VK-Finder Project
Chat Bot for VK Company to help you find your significant other.

The bot searches for people matching the conditions based on user information from VK:
- age,
- sex,
- city,
- family status.

For those people who meet the requirements, the user shows the top 3 popular profile photos in the chat along with a link to the found person.
Popularity is determined by the number of likes and comments.

---

### Built with:

[<img src="https://img.shields.io/badge/python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=Python">](https://www.python.org/)
[<img src="https://img.shields.io/badge/PostgreSQL-14.6-blue?style=for-the-badge&logo=PostgreSQL">](https://www.postgresql.org/)
[<img src="https://img.shields.io/badge/SQLAlchemy-2.0.4-blue?style=for-the-badge">](https://docs.sqlalchemy.org/en/20/)
[<img src="https://img.shields.io/badge/Alembic-1.9.4-blue?style=for-the-badge">](https://alembic.sqlalchemy.org/en/latest/)

---

### Project setup steps

**1. Project requirements**
```python
pip install -r requirements.txt
```

**2. Create a database *vk_finder* or connect to an existing one.**
> createdb -U <OWNER_NAME> vk_finder

**3. Create** *.env* **file with environment variables in folder path:**
> vk_finder/config/.env

You need to specify *VK_USER_TOKEN, VK_GROUP_TOKEN and DSN*.

[User token can be obtained here](https://vkhost.github.io/)

*DSN* is a data source name to your PostgreSQL database.
> postgresql://demo:demo@localhost:port/db

**4. Table migrations to the database.**

Create an initial Alembic migration for an existing database.

*Run commands in terminal*
```python
alembic init vk_finder/migrations
```
---
#### Configuration of the env.py file
Open the file in vk_finder/migrations/env.py and add the following changes to it.


We import the libraries to get the environment variables, run the necessary methods to get the variables and set them in the settings:
```python
import os

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

config = context.config
config.set_main_option('sqlalchemy.url', os.getenv('DSN'))
```

Adding a MetaData object to our model to support "autogeneration"
```python
from vk_finder.database.models import Base


target_metadata = Base.metadata
```
---

To complete the migrations, run the following commands in the terminal
```python
alembic revision --autogenerate -m "Init migration"
alembic upgrade head
```
