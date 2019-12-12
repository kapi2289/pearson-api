import re


class Product:
    def __init__(self, j, api):
        self.uid = j.get("id")
        self.name = j.get("name")
        self.type = j.get("type")
        self.url = j.get("access", {}).get("student", {}).get("url")
        self.id = re.search("login/(.+?)\?", self.url).group(1)
        self.api = api
        self.login()

    def login(self):
        r = self.api.get(self.url, as_json=False)
        self.api.get("https://myenglishlab.pearson-intl.com/sso/login", as_json=False, cookies={"requested_url": r.url})
