import requests
import urllib.request
import json
import re


from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from teachable.teachable_authorizer import TeachableAuthorizer


class Teachable(TeachableAuthorizer):
    def __init__(self, key: str):
        super().__init__(key)
        self.months = {"styczeń": 1, "luty": 2, "marzec": 3, "kwiecień": 4, "maj": 5, "czerwiec": 6, "lipiec": 7,
                       "sierpień": 8, "wrzesień": 9, "październik": 10, "listopad": 11, "grudzień": 12}

    def get_all_courses(self, page: int = 1, per: int = 30) -> dict:
        """
        https://docs.teachable.com/reference/listcourses
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses?page={page}&per={per}"
        response = self._send_request(url)
        return response.json()

    def get_course(self, course_id) -> dict:
        """
        https://docs.teachable.com/reference/showcourse
        :param course_id:
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses/{course_id}"
        response = self._send_request(url)
        return response.json()

    def get_lecture(self, course_id, lecture_id) -> dict:
        """
        https://docs.teachable.com/reference/showlecture
        :param course_id:
        :param lecture_id:
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses/{course_id}/lectures/{lecture_id}"
        response = self._send_request(url)
        return response.json()

    def get_video_data(self, course_id, lecture_id, video_id) -> dict:
        """
        https://docs.teachable.com/reference/showlecture
        :param course_id:
        :param lecture_id:
        :param video_id:
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses/{course_id}/lectures/{lecture_id}/videos/{video_id}"
        response = self._send_request(url)
        return response.json()

    @staticmethod
    def get_sales_page_url(course_id: int) -> str:
        return f"https://www.newgradvets.com/courses/enrolled/{course_id}"

    def get_upcoming_teachable_course(self, standardized_cname, course_data):
        """
        `standardized_cname` must be a stripped, split by '(' string converted by `self._to_lower_alphanumeric()` method.
        :param standardized_cname:
        :param course_data:
        :return:
        """
        upcoming_course = None
        upcoming_course_date = date(year=2099, month=1, day=1)

        # 1. find all courses matching the name
        matching_courses = []
        for course in course_data["courses"]:
            standardized_current_cname = self.to_lower_alphanumeric(course["name"])
            if standardized_current_cname.startswith(standardized_cname):
                matching_courses.append(course)

        # 2. go through all matching courses and select the first upcoming course
        for m_course in matching_courses:
            today_date = date.today()
            name_split = m_course["name"].strip().split(" ")
            try:
                month = self.months[name_split[-2].lower()]
                year = int(name_split[-1])
            except (KeyError, ValueError):
                continue
            course_date = date(year=year, month=month, day=1) + relativedelta(months=1)
            delta_current = upcoming_course_date - today_date
            delta_course = course_date - today_date
            if delta_course.days < 0:
                continue
            if delta_current.days > delta_course.days:
                upcoming_course = m_course
                upcoming_course_date = course_date

        return upcoming_course

    def to_lower_alphanumeric(self, string):
        return re.sub(r'[^a-z0-9ąęćńłóśżź]', '', string.lower())

    def get_static_url(self, url, filename):
        urllib.request.urlretrieve(url, filename)

    def _send_request(self, url, use_json: bool = True):
        response = requests.get(url, headers=self._build_headers())
        if response.status_code != 200:
            if use_json:
                raise Exception(f"GET Request returned code {response.status_code}. Details:\n{response.json()}")
            else:
                raise Exception(f"GET Request returned code {response.status_code}. Details:\n{response.content}")
        return response

    def _build_headers(self):
        return {
            "accept": "application/json",
            "apiKey": self.key
        }
