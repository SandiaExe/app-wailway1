import redis
import os

r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

# --- FUNCIONES PARA EL VOCABULARIO (Usa Redis Hashes) ---

def add_vocabulary(word, definition):
    """Guarda una palabra y su significado en un Hash de Redis llamado 'user_vocab'"""
    r.hset("user_vocab", word, definition)

def get_vocabulary():
    """Retorna todo el diccionario guardado por el usuario"""
    return r.hgetall("user_vocab")


# --- FUNCIONES PARA LOS ERRORES (Usa Redis Strings como contadores) ---

def increment_error_count():
    """Incrementa en 1 el contador de errores del usuario"""
    r.incr("user_errors")

def get_error_count():
    """Obtiene el número total de errores registrados"""
    count = r.get("user_errors")
    return int(count) if count else 0
