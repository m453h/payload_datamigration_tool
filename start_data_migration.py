#!/usr/bin/python3

from payload_auth import Auth
from payload_api import PayloadAPI
import glob, os

folder_path = 'collections'
source_auth = Auth("SOURCE")
sink_auth = Auth("SINK")

if source_auth.login() and sink_auth.login():
    print("User is authenticated...Source [{}]".format((source_auth.endpoint)))
    print("User is authenticated...Sink [{}]".format((sink_auth.endpoint)))
    site = PayloadAPI(source_auth, sink_auth)

    files = glob.glob(os.path.join(folder_path, '*'))
    for file_path in files:
        site.import_data(file_path)