import requests
import os
from dotenv import load_dotenv

class Auth:

  def __init__(self, type):
    load_dotenv()
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
        return True
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    return False
  
  @property
  def session(self):
    return self.req
  
  @property
  def endpoint(self):
     return self.api_url
