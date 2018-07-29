import requests, json
from requests import auth

def call_KNIME_WebService(serviceName, values, user, pw, baseURL="http://knime05:8080/webportal/rest/v4/repository/"):
    url = "%s%s:job-pool"%(baseURL, serviceName)
    authd = auth.HTTPBasicAuth(user, pw)
    reqbody = json.dumps({"input-data": {"jsonvalue":qry}})
    resp = requests.post(url, auth=authd, data = reqbody, headers={"Content-Type":"application/json"})
    if resp.ok and resp.status_code == 200:
        outvs = resp.json()['outputValues' ]
        return tuple(outvs.values())
    raise RuntimeError(resp.status_code)

#o co chodzi z tym smiles? to jakiś parametr?
qry = dict(smiles=["clccccc1N", "c1ccccc10"])

values = call_KNIME_WebService("LifeSciences/demos/WebServices/1_BasicDescriptors", qry, user, pw)

values[0]


