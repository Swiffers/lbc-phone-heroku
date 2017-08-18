import redis
from rq import Worker, Queue, Connection


listen = ['high', 'default', 'low']

conn = redis.from_url("REDIS_CO_STRING")

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

