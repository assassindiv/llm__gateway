import redis, time
r = redis.Redis(host='localhost', port=6379)

start = time.time()
val = r.get("chat_cache:78d74b323d1a544921cc9f60dd7bf43c2dff7139e522d54ed7ca4244cecc8486")
print(f"Raw Redis fetch: {(time.time()-start)*1000:.2f}ms")