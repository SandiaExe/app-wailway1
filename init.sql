CREATE TABLE IF NOT EXISTS chat_history (

    id SERIAL PRIMARY KEY,

    role VARCHAR(20),

    message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
