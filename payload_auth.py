from datetime import datetime
from http.cookiejar import Cookie
import requests,pickle
import os
from dotenv import load_dotenv

class Auth:

  def __init__(self, type):
    load_dotenv()
    self.type = type
    if type == "SOURCE":
      self.username = os.getenv("SOURCE_USERNAME")
      self.password = os.getenv("SOURCE_PASSWORD")
      self.api_url = os.getenv("SOURCE_API_URL")
    elif type == "SINK":
      self.username = os.getenv("SINK_USERNAME")
      self.password = os.getenv("SINK_PASSWORD")
      self.api_url = os.getenv("SINK_API_URL")
    self.req = requests.Session()

  def login(self):
    has_cookies = False
    cookies_path = f"tmp/{self.type}.cookies"
    try:
      with open(cookies_path, 'rb') as f:
        self.req.cookies.update(pickle.load(f))
        has_cookies = True
        if self.is_expired_session():
          has_cookies = False
    except FileNotFoundError:
      pass

    if not has_cookies:
      try:
          url = self.api_url + "/users/login"

          headers = {
              "Content-Type": "application/json",
          }

          payload = {
              "email": self.username,
              "password": self.password
          }

          response = self.req.post(url, headers=headers, json=payload)
          response.raise_for_status()
          with open(cookies_path, 'wb') as f:
            pickle.dump(self.req.cookies, f)
          return True
      except requests.exceptions.RequestException as err:
          print(f"An error occurred: {err}")
      return False
    else:
      return True
  
  @property
  def session(self):
    return self.req
  
  @property
  def endpoint(self):
     return self.api_url

  def is_expired_session(self):
    current_time = int(datetime.now().timestamp())
    for cookie in self.req.cookies:
      if isinstance(cookie, Cookie):
        if not cookie.is_expired(current_time):
            return True
    return False