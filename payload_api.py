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
         if collection.get('name') != 'donors':
            continue
         self.get_collections(collection)

  def get_collections(self, collection, page_number=1):
      try:
          name = collection.get('name')
          url = f"{self.source.endpoint.rstrip('/')}/{name}?page={page_number}"
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
      name = collection.get('name')
      upload_fields = collection.get("upload_fields")
      url = f"{self.sink.endpoint.rstrip('/')}/{name}"
      # print(json.dumps(data, indent=4))

      #Upload resource
      for field in upload_fields:
        data[field] = self.upload_file(data[field])

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
    response_data = upload_reponse.json()
    
    if upload_reponse.status_code == 200:
      try:
        return upload_reponse['doc']['id']
      except KeyError:
        return None
    elif upload_reponse.status_code == 400:
        try:
          errors = (response_data['errors'])
          for error in errors:
             error_items = error.get('data').get('errors')
             for error_item in error_items:
              if error_item.get('field') == 'filename'\
                  and error_item.get('message') == 'Value must be unique':
                 print("File already uploaded...getting original file")
                 return self.get_media_file_id(data.get('filename'))
        except KeyError:
           return None
      

  def get_media_file_id(self, filename):
    url = f"{self.sink.endpoint.rstrip('/')}/media"
    params = {
        "where[filename][equals]": filename
    }
    response = requests.get(url, 
                            headers={"Content-Type": "application/json"},
                            params=params)
    response = response.json()
    try:
       return response['docs'][0]['id']
    except KeyError:
       return None