import redis
import os

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True
)

def get_cached_response(prompt):

    return r.get(prompt)

def set_cached_response(prompt, response):

    r.set(prompt, response, ex=3600)
