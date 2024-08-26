import requests
import json
class PayloadAPI:

  def __init__(self, source, sink):
     self.source = source
     self.sink = sink
     self.collections = ['donors']

  def import_data(self, collections_path):
    with open(collections_path, 'r') as file:
      data = json.load(file)
      for collection in data['collections']:
         self.get_collections(collection.get('name'))

  def get_collections(self, collection, page_number=1):
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
      print(json.dumps(data, indent=4))

      '''#Upload Image resource
      data['logo'] = self.upload_file(data['logo'])'''
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

  def upload_file(self, data):
    upload_reponse = requests.post(
        f"{self.sink.endpoint.rstrip('/')}/media",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data),
      )
    upload_reponse = upload_reponse.json()
    try:
      return upload_reponse['doc']['id']
    except KeyError:
       return None