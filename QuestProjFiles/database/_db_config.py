from sqlalchemy import create_engine

DB_USERNAME = "quests_remote"
DB_PASSWORD = "questProject11-remote"
DB_HOST = "projectswhynot.site"
DB_PORT = "11459"
DB_NAME = "quests"
engine = create_engine("mysql+pymysql://" + DB_USERNAME + ":" + DB_PASSWORD + f"@{DB_HOST}:{DB_PORT}/" + DB_NAME + "?charset=utf8",
                       pool_size=10,
                       max_overflow=20,
                       echo=True)