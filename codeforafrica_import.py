from payload_auth import Auth
from payload_api import PayloadAPI

source_auth = Auth("SOURCE")
sink_auth = Auth("SINK")

if source_auth.login() and sink_auth.login():
    print("User is authenticated...Source [{}]".format((source_auth.endpoint)))
    print("User is authenticated...Sink [{}]".format((sink_auth.endpoint)))
    cfa_site = PayloadAPI(source_auth, sink_auth)
    cfa_site.import_data('collections/codeforafrica.json')
