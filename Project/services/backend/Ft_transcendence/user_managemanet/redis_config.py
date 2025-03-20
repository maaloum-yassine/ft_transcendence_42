import redis , os

redis_client = redis.StrictRedis(host= os.getenv('SERVR_CACHE'), port=os.getenv('PORT_CACHE'), db=0, decode_responses=True)

