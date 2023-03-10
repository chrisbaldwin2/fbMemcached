import pymemcache.client.base

class MemcachedInterface:
    def __init__(self, host='localhost', port=11211):
        self.client = pymemcache.client.base.Client((host, port))
    
    def clear(self):
        self.client.flush_all()

    def get(self, key):
        value = self.client.get(key)
        if value is None:
            return None
        return value.decode('utf-8')
    
    def set(self, key, value, ttl=0):
        self.client.set(key, value.encode('utf-8'), expire=ttl)
    
    def delete(self, key):
        self.client.delete(key)

    def __del__(self):
        self.client.close()
