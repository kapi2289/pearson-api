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
        tried_again = False

        for i in range(5):
            r_solve = self.api.get("https://myenglishlab.pearson-intl.com/activities/{}/0/solve".format(activity_id),
                                   as_json=False)
            soup = bs(r_solve.text, "html.parser")

            task_content = soup.find("div", {"class": "taskContent"})
            if task_content is not None:
                inputs = [e["name"] for e in task_content.find_all() if
                          e.get("name") is not None]
            else:
                inputs = []

            data = {a: "" for a in inputs}
            data.update({
                "isPopup": 0,
                "timeSpent": 1000
            })

            r_report = self.api.get("https://myenglishlab.pearson-intl.com/activities/{}/0/report".format(activity_id),
                                    as_json=False)

            pattern_answers = "var correctAnswers = (.+?);"

            if "correctAnswers = {" in r_report.text:
                correct = re.search(pattern_answers, r_report.text).group(1)
                return json.loads(correct)
            if "Show answers" in r_report.text:
                r_show_answers = self.api.get(
                    "https://myenglishlab.pearson-intl.com/activities/{}/0/show_answers".format(activity_id),
                    as_json=False)
                correct = re.search(pattern_answers, r_show_answers.text).group(1)
                return json.loads(correct)
            elif tried_again:
                self.api.post("https://myenglishlab.pearson-intl.com/activities/{}/submit".format(activity_id),
                              as_json=False, data=data)
                tried_again = False
            elif "tryAgain" in r_report.text:
                url = re.search("<a id=\"tryAgain\" class=\"button\" href=\"(.+?)\"", r_report.text).group(1)
                url = "https://myenglishlab.pearson-intl.com" + url
                r_try_again = self.api.get(url, as_json=False)
                new_activity_id = re.search("activities/(.+?)/0", r_try_again.url)
                if new_activity_id:
                    activity_id = new_activity_id.group(1)
                tried_again = True
            else:
                self.api.post("https://myenglishlab.pearson-intl.com/activities/{}/submit".format(activity_id),
                              as_json=False, data=data)
