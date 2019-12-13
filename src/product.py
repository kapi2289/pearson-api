import json
import re

from bs4 import BeautifulSoup as bs


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

    def get_answers(self, activity_id):
        for i in range(5):
            r_solve = self.api.get("https://myenglishlab.pearson-intl.com/activities/{}/0/solve".format(activity_id),
                                   as_json=False)
            soup = bs(r_solve.text, "html.parser")
            inputs = [e["name"] for e in soup.find("div", {"class": "taskContent"}).find_all() if
                      e.get("name") is not None]

            data = {a: "" for a in inputs}
            data.update({
                "isPopup": 0,
                "timeSpent": 1000
            })

            r_report = self.api.get("https://myenglishlab.pearson-intl.com/activities/{}/0/report".format(activity_id),
                                    as_json=False)

            pattern_answers = "var correctAnswers = (.+?);"

            if "correctAnswers" in r_report.text:
                correct = re.search(pattern_answers, r_report.text).group(1)
                return json.loads(correct)
            if "Show answers" in r_report.text:
                r_show_answers = self.api.get(
                    "https://myenglishlab.pearson-intl.com/activities/{}/0/show_answers".format(activity_id),
                    as_json=False)
                correct = re.search(pattern_answers, r_show_answers.text).group(1)
                return json.loads(correct)
            elif "Try again" in r_report.text:
                url = re.search("<a id=\"tryAgain\" class=\"button\" href=\"(.+?)\"", r_report.text).group(1)
                url = "https://myenglishlab.pearson-intl.com" + url
                self.api.get(url, as_json=False)
            else:
                self.api.post("https://myenglishlab.pearson-intl.com/activities/{}/submit".format(activity_id),
                              as_json=False, data=data)
