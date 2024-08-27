import requests
import json
class PayloadAPI:
  """
    The `PayloadAPI` class is responsible for handling data importation between a source and a sink, 
    particularly focusing on specific collections and their associated files.
  """

  def __init__(self, source, sink):
    """
      Initializes a new instance of the `PayloadAPI` class, setting up the necessary source and sink configurations.

      Parameters:
      -----------
      source : Auth
        The source authentication instance, used to authenticate and interact with the source API.
      sink : Auth
        The sink authentication instance, used to authenticate and interact with the sink API.
    """
    self.source = source
    self.sink = sink
    self.collections = ['donors']

  def import_data(self, collections_path):
    """
      Imports data from a JSON file, filtering and processing specific collections.

      Parameters:
      -----------
      collections_path : str
          The file path to the JSON file containing the data to be imported.

      Actions:
      --------
      - Opens the specified JSON file and loads the data.
      - Iterates through the collections in the file, processing only those named 'partners'.
      - Calls `get_collections` to retrieve and process the data for the specified collection.
    """
    with open(collections_path, 'r') as file:
      data = json.load(file)
      for collection in data['collections']:
         if collection.get('name') != 'partners':
            continue
         self.get_collections(collection)

  def get_collections(self, collection, page_number=1):
    """
    Retrieves paginated data from the source API for a given collection and processes each document.

    Parameters:
    -----------
    collection : dict
        A dictionary representing the collection to be processed.
    page_number : int, optional
        The page number to retrieve, default is 1.

    Actions:
    --------
    - Constructs the URL for the API request using the collection name and page number.
    - Sends a GET request to the source API to retrieve the collection data.
    - Iterates over the documents in the retrieved data and posts each one to the sink API using `post_collection`.
    - Recursively fetches additional pages if more pages are available.

    Returns:
    --------
    bool: `True` when the process is complete.
    """
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
    """
      Posts a document to the sink API, uploading associated files as needed.

      Parameters:
      -----------
      data : dict
        The document data to be posted to the sink API.

      collection : dict
            The collection information, including any upload fields.

      Actions:
      --------
      - Constructs the API endpoint URL for posting the document.
      - For each field in `upload_fields`, uploads the associated file using `upload_file`.
      - Sends a POST request to the sink API with the document data.
      - Prints the response data or an error message if the request fails.
    """
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
    """
      Handles the uploading of files to the sink API and manages scenarios where the file already exists.

      Parameters:
      -----------
      data : dict
        The file data to be uploaded.

      Actions:
      --------
      - Sends a POST request to the sink API to upload the file.
      - If the file already exists (checked by unique filename), retrieves the existing file's ID using `get_media_file_id`.
      - Returns the ID of the uploaded file or the existing file.

      Returns:
      --------
      str or None: The ID of the uploaded file, or `None` if an error occurs or the file ID cannot be retrieved.
    """
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
    """
      Retrieves the media file ID from the sink API based on the filename, useful for avoiding duplicate uploads.

      Parameters:
      -----------
      filename : str
        The name of the file for which to retrieve the ID.

      Actions:
      --------
      - Sends a GET request to the sink API to search for the file by filename.
      - If the file is found, returns the file's ID.

      Returns:
      --------
      str or None: The ID of the file, or `None` if the file is not found or an error occurs.
    """
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