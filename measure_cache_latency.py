import time, requests, redis, hashlib, json

r = redis.Redis(host="redis", port=6379)
headers = {"x-api-key": "test-key-123"}
payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "What is AI?"}]
}

# Clear cache
cache_source = {"model": payload["model"], "messages": payload["messages"]}
cache_key = "chat_cache:" + hashlib.sha256(
    json.dumps(cache_source, sort_keys=True).encode()
).hexdigest()
r.delete(cache_key)

# Miss
res1 = requests.post("http://localhost:8000/chat", json=payload, headers=headers)
print(f"Miss - X-Cache: {res1.headers.get('X-Cache')}")

# Hit
res2 = requests.post("http://localhost:8000/chat", json=payload, headers=headers)
print(f"Hit  - X-Cache: {res2.headers.get('X-Cache')}")

# Raw Redis speed
start = time.time()
r.get(cache_key)
print(f"Raw Redis fetch: {(time.time()-start)*1000:.2f}ms")
