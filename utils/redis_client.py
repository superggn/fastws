import os

import redis

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
IS_PROD_ENV = os.environ.get('FASTWS_ENV') == 'PROD'
# IS_TEST_ENV = not IS_PROD_ENV
REDIS_DB = 0 if IS_PROD_ENV else 1

REDIS_LIST_LEN = 50


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # 使用 singleton 模式，全局只创建一个 connection
        if cls.conn:
            return cls.conn
        cls.conn = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        # clear all keys in redis, for testing purpose
        if IS_PROD_ENV:
            raise Exception("You can not flush redis in production environment")
        conn = cls.get_connection()
        conn.flushdb()


conn = RedisClient.get_connection()


def cache_get(key):
    res = conn.get(key)
    if type(res) == bytes:
        res = res.decode()
    return res


def cache_lpush(key, input_str):
    conn.lpush(key, input_str)
    conn.ltrim(key, 0, REDIS_LIST_LEN - 1)


def cache_get_list(key):
    bytes_ls = conn.lrange(key, 0, REDIS_LIST_LEN - 1)
    str_ls = [item.decode() for item in bytes_ls]
    return str_ls


def cache_set(key, value, ttl=None):
    conn.set(key, value, ttl)
