#!/usr/bin/python3

from datetime import datetime
from http.cookiejar import Cookie
import requests,pickle
import os
from dotenv import load_dotenv

class Auth:
  """
  The `Auth` class manages user authentication, including login and session management, 
  by handling environment-based configurations and session cookies.
  """

  def __init__(self, type):
    """
    Initializes a new instance of the class, setting up the necessary configuration 
    based on the provided type.

    Parameters:
    type (str): Specifies the type of configuration to load. 
                Accepted values are "SOURCE" or "SINK".

    Actions:
    - Loads environment variables from a `.env` file using `load_dotenv()`.
    - Sets up `username`, `password`, and `api_url` attributes based on the `type` parameter:
      - If `type` is "SOURCE":
          - Loads `SOURCE_USERNAME`, `SOURCE_PASSWORD`, and `SOURCE_API_URL` from environment variables.
      - If `type` is "SINK":
          - Loads `SINK_USERNAME`, `SINK_PASSWORD`, and `SINK_API_URL` from environment variables.
    - Initializes a `requests.Session` object and assigns it to the `req` attribute for managing HTTP requests.
    """
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
    """
    Handles the login process for the user, managing session cookies to maintain a logged-in state.

    Actions:
    - Checks for existing session cookies in the `tmp/` directory based on the `type` of instance.
    - If cookies are found and the session is valid, the method skips the login process.
    - If no cookies are found or the session is expired:
      - Sends a login request to the API using the stored `username` and `password`.
      - Stores the session cookies in a file for future use.
    - Handles any exceptions that occur during the login process.

    Returns:
    bool: 
        - `True` if login is successful or valid session cookies exist.
        - `False` if the login process fails.

    Workflow:
    - The method first attempts to load session cookies from a file (`tmp/{self.type}.cookies`).
    - If cookies are loaded successfully, it checks whether the session is expired using `is_expired_session()`.
    - If no valid cookies are found, it constructs a login request to the API.
    - The request includes the `username` and `password` as JSON payload and sends the request with the appropriate headers.
    - If the login is successful, the session cookies are saved for future use.
    - If the request fails, an error is logged, and the method returns `False`.
    """
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
    """
      Returns the current `requests.Session` object.
    """
    return self.req
  
  @property
  def endpoint(self):
     """
     Returns the current API endpoint URL.
     """
     return self.api_url

  def is_expired_session(self):
    """
    Checks if the current session is expired by evaluating the cookies stored in the session.

    Actions:
    - Retrieves the current timestamp.
    - Iterates through the cookies in the session.
    - For each cookie:
      - Verifies if it is an instance of the `Cookie` class.
      - Checks if the cookie has expired based on the current time.
    
    Returns:
    bool:
        - `True` if there is at least one valid (non-expired) cookie, indicating that the session is not expired.
        - `False` if all cookies are expired or if there are no valid cookies, indicating that the session is expired.

    Workflow:
    - The method fetches the current time as a Unix timestamp.
    - It then iterates over the session cookies.
    - For each cookie, it checks if the cookie is an instance of `Cookie`.
    - If a valid cookie (one that is not expired) is found, the method returns `True`,
      indicating that the session is still active.
    - If no valid cookies are found, the method returns `False`, indicating that the session is expired.
    """
    current_time = int(datetime.now().timestamp())
    for cookie in self.req.cookies:
      if isinstance(cookie, Cookie):
        if not cookie.is_expired(current_time):
            return True
    return False