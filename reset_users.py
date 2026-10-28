
from main import engine, UserDB
from sqlalchemy import inspect

# Sirf users table delete hogi
UserDB.__table__.drop(bind=engine, checkfirst=True)

# Nayi users table create hogi
UserDB.__table__.create(bind=engine)

print("Users table recreated successfully!")

# Verify tables and columns
inspector = inspect(engine)
print("Tables:", inspector.get_table_names())
print(
    "Users columns:",
    [column["name"] for column in inspector.get_columns("users")]
)
print(
    "Tasks columns:",
    [column["name"] for column in inspector.get_columns("tasks")]
)
