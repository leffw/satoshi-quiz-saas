from cachetools import cached, TTLCache
import requests

class Hygraph:
    
    def __init__(self, url: str):
        self.url = url

    @cached(cache=TTLCache(maxsize=1, ttl=(60 * 60) * 24))
    def call(self, query: str, variables=None):
        data = {
            'query': query,
            'variables': variables
        }
        return requests.post(self.url, json=data).json().get("data")
        