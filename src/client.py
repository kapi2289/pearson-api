import requests

from .product import Product


class Client:

    def __init__(self, username, password):
        self.session = requests.session()
        self.token = None
        self.login(username, password)

    def _request(self, url, method=None, as_json=True, try_again=True, **kwargs):
        headers = {}
        if self.token:
            headers = {"Authorization": "Bearer {}".format(self.token)}
            headers.update(kwargs.get("headers", {}))
        headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"})
        r = self.session.request(method, url, headers=headers, **kwargs)
        if try_again:
            try:
                r.raise_for_status()
            except requests.HTTPError:
                self.refresh()
                self._request(url, method, as_json=as_json, try_again=False, **kwargs)
        else:
            r.raise_for_status()
        if as_json:
            return r.json()
        else:
            return r

    def post(self, url, as_json=True, try_again=True, **kwargs):
        return self._request(url, "POST", as_json=as_json, try_again=try_again, **kwargs)

    def get(self, url, as_json=True, try_again=True, **kwargs):
        return self._request(url, "GET", as_json=as_json, try_again=try_again, **kwargs)

    def login(self, username, password):
        data = {
            "username": username,
            "password": password,
        }
        r = self.post("https://english-dashboard.pearson.com/api/dashboard/v1/users/sign-in", json=data)

        code = r.get("result")
        url_check = "https://english-dashboard.pearson.com/api/dashboard/v1/users/status/sign-in/{}".format(code)
        for _ in range(30):
            r_check = self.get(url_check, try_again=False)
            result = r_check.get("result", {})
            if result.get("status") == "COMPLETED":
                if result.get("details") == "SUCCESS":
                    r_gateway = self.post("https://sso.rumba.pearsoncmg.com/sso/gateway", as_json=False,
                                          data=result.get("gatewayParameters"))
                    self.token = result.get("token")
                    print("Success!")
                    break
                break
        else:
            raise TimeoutError("Request timed out!")

    def refresh(self):
        r = self.get("https://english-dashboard.pearson.com/api/dashboard/v1/token/refresh", try_again=False)
        token = r.get("result", {}).get("token")
        if token:
            self.token = token

    def get_products(self):
        r = self.get("https://english-dashboard.pearson.com/api/dashboard/v1/user/products")
        products = r.get("result", {}).get("products", [])
        return [Product(p, self) for p in products]