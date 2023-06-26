import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
YOOTOKEN = str(os.getenv("YOOTOKEN"))
ADMIN = 716775112

IP = str(os.getenv("IP"))
PGUSER = str(os.getenv("PGUSER"))
PGPASS = str(os.getenv("PGPASS"))
DB = str(os.getenv("DB"))

POSTGRES_URI = f"postgresql://{PGUSER}:{PGPASS}@{IP}/{DB}"