from sqlalchemy import create_engine, text
import os

#DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(os.getenv("DATABASE_URL"))

def init_db():

    with engine.connect() as conn:

        conn.execute(text("""

            CREATE TABLE IF NOT EXISTS chat_history (

                id SERIAL PRIMARY KEY,

                role VARCHAR(20),

                message TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

        """))

        conn.commit()

def save_message(role, message):

    with engine.connect() as conn:

        conn.execute(
            text(
                """
                INSERT INTO chat_history (role, message)
                VALUES (:role, :message)
                """
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
