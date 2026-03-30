from cachetools import TTLCache

# In-memory cache: Stores up to 1000 queries, expires after 1 hour (3600 seconds)
# In a distributed production system, this would be backed by Redis
rag_cache = TTLCache(maxsize=1000, ttl=3600)
