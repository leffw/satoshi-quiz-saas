import requests

class MemberStack:
    
    def __init__(self, api_key: str):
        self.url = "https://api.memberstack.com"
        self.__api_key = api_key
    
    def call(self, method: str, path: str, params=None, json=None):
        headers = { "X-API-KEY": self.__api_key }
        return requests.request(
            method=method, 
            url=self.url + path, 
            json=json, 
            params=params, 
            headers=headers
        ).json()
    
    def get_member(self, id: str) -> dict:
        return self.call("GET", f"/v1/members/{id}")