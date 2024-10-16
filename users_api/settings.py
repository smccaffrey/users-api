import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.environ.get("ENV", "")
IS_TEST = ENV == "local"

DATABASE_URL = os.environ.get("DATABASE_URL")
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
