import requests
import json
class PayloadAPI:

  def __init__(self, source, sink):
     self.source = source
     self.sink = sink
     self.collections = ['donors']

  def import_data(self):
    for collection in self.collections:
      self.get_collections(collection, 1)

  def get_collections(self, collection, page_number):
      try:
          url = f"{self.source.endpoint.rstrip('/')}/{collection}?page={page_number}"
          response = self.source.session.get(url)
          if response.status_code == 200:
              data = response.json()
              docs = data.get("docs")
              for doc in docs:
                 self.post_collection(doc, collection)
              if page_number < data.get("totalPages"):
                  return self.get_collections(collection, data.get("page") + 1)
          else:
              print(f"Failed to retrieve data. Status code: {response.status_code}")
              return True
      except requests.exceptions.RequestException as err:
          print(f"An error occurred: {err}")

      return True
  
  def post_collection(self, data, collection):
    try:
      url = f"{self.sink.endpoint.rstrip('/')}/{collection}"
      response = requests.post(
          url,
          headers={"Content-Type": "application/json"},
          data=json.dumps(data),
          cookies=None
      )
      data = response.json()
      print(data)
    except requests.exceptions.RequestException as err:
      print(f"An error occurred: {err}")