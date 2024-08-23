import requests



import requests
import os
from dotenv import load_dotenv

class CodeforAfricaAPI:

  def __init__(self, session):
     self.session = session
     self.collections = ['tag']

  def import_data(self):
    for collection in self.collections:
        try:
            url = f"{self.api_url.rstrip('/')}/{collection.lstrip('/')}"
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("Data:", data)
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")



