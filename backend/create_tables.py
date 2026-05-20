from database import engine
from models import Base, PromptHistory  # noqa: F401 — import so create_all sees the table

Base.metadata.create_all(bind=engine)

print("All tables created successfully")
