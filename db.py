from sqlalchemy import create_engine, text
import os

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DB_URL)

def save_message(role, message):

    with engine.connect() as conn:

        conn.execute(
            text(
                "INSERT INTO chat_history (role, message) VALUES (:role, :message)"
            ),
            {
                "role": role,
                "message": message
            }
        )

        conn.commit()

def get_history():

    with engine.connect() as conn:

        result = conn.execute(
            text(
                """
                SELECT role, message
                FROM chat_history
                ORDER BY id ASC
                """
            )
        )

        return result.fetchall()
