import requests
import json
from onshape_client.client import Client
from onshape_client.onshape_url import OnshapeElement
import warnings
import time 


class OnshapeAPI: 
    def __init__(self, api_access, api_secret):
        self.base = 'https://cad.onshape.com'
        # define onshape client
        self.client = self._initialize_client(api_access, api_secret)

    def _initialize_client(self, api_access, api_secret):
        return Client(configuration={
                        "base_url": self.base,
                        "access_key": api_access,
                        "secret_key": api_secret
                    })

    def _url_elem(self, url):
        """
        get onshape url element 
        """
        element = OnshapeElement(url)
        base = element.base_url
        did = element.did
        wvm = element.wvm
        wid = element.wvmid
        eid = element.eid

        return did, wid, eid, wvm

    def _build_url(self, url_template, did, wid, eid):
        return url_template.replace('did', did).replace('wid', wid).replace('eid', eid)

    def createPartStudioTranslation(url, filename): 
        """
        API call type: `POST`
        Create assembly translation by document ID, workspace or version ID, and tab ID.
        More details can be found in https://cad.onshape.com/glassworks/explorer/#/Assembly/translateFormat

        - `client` (Required): the Onshape client configured with your API keys
        - `url` (Required): the url of the Onshape document you would like to make this API call to
        - `params`: a dictionary of the following parameters for the API call
        - `payload` (Required): a dictionary of the payload body of this API call; a template of the body is shown below:         
        - `show_response`: boolean: do you want to print out the response of this API call (default: False)
        """
        did, wid, eid, wvm = self._url_elem(url)
        method = "POST" 
        url_ext = "/api/partstudios/d/did/wv/wid/e/eid/translations"
        fixed_url = self._build_url(url_ext, did, wid, eid) 
        fixed_url = fixed_url.replace('wv', wvm)
        
        headers = {"Accept": "application/vnd.onshape.v2+json;charset=UTF-8;qs=0.2", "Content-Type": "application/json"}
        params  = {}
        payload = {
                    "formatName": "STEP",
                    "elementId": eid,
                    "storeInDocument": False,
                    "destinationName": filename,
                    "unit": "inch"
                }
        try:
            response = self.client.api_client.request(method, url=self.base+fixed_url, 
                                                        query_params=params, 
                                                        headers=headers, 
                                                        body=payload)
            parsed = json.loads(response.data)
            return parsed
        except:
            return None

    def get_version(self, url):

        version_url = '/api/documents/d/did/versions'
        did, wid, eid, _ = self._url_elem(url)
        method = 'GET'

        # onshape api params
        headers={
            "Accept": "application/json;charset=UTF-8; qs=0.09", 
            "Content-Type": "application/json"
        }

        version_url = version_url.replace('did', did)
        

        # get api response
        response = self.client.api_client.request(method, 
                                            url=self.base + version_url, 
                                            query_params={}, 
                                            headers=headers, 
                                            body={})
        parsed = json.loads(response.data)
        # parent version id 
        version_id = parsed[0]['id']
        
        return version_id

    def create_version(self, url, version_name='test'): 

        version_url = '/api/documents/d/did/versions'
        did, wid, eid, _ = self.url_elem(url)
        method = 'POST'

        # parent version id 
        version_id = self.get_version(url)

        # onshape api params
        request_body = {
                "documentId": did,
                "name": version_name,
                "readOnly": 'true',
                "isRelease": 'true',
                "versionId": version_id,
                }
        
        headers={
            "Accept": "application/json;charset=UTF-8; qs=0.09", 
            "Content-Type": "application/json"
        }

        version_url = version_url.replace('did', did)
        
        # get api response
        response = self.client.api_client.request(method, 
                                                url=self.base + version_url, 
                                                query_params={}, 
                                                headers=headers, 
                                                body=request_body)
        parsed = json.loads(response.data)
        # new version id 
        version_id = parsed['id']
        return version_id


    def create_branch(self, url, child_version_id, branch_name='child branch'):
        branch_url = '/api/documents/did/workspaces'
        did, wid, eid, _ = self._url_elem(url)
        method = 'POST'
        headers={
            "Accept": "application/json;charset=UTF-8; qs=0.09", 
            "Content-Type": "application/json"
            }
        branch_url = branch_url.replace('did', did)

        request_body = {"parentWorkspaceId": child_version_id,
                        "name": branch_name
                        }
        response = self.client.api_client.request(method, 
                                                url=self.base + branch_url, 
                                                query_params={}, 
                                                headers=headers, 
                                                body=request_body)
        
    def get_branch_url(self, url):
        branch_url = '/api/documents/did/workspaces'
        did, wid, eid, _ = self._url_elem(url)
        method = 'GET'
        headers={
            "Accept": "application/json;charset=UTF-8; qs=0.09", 
            "Content-Type": "application/json"
            }
        branch_url = branch_url.replace('did', did)
        response = self.client.api_client.request(method, 
                                                url=self.base + branch_url, 
                                                query_params={}, 
                                                headers=headers, 
                                                body={})
        
        parent_workspace_id = wid
        workspace_info = json.loads(response.data)
        num_of_child = 0 
        for data in workspace_info:
            if data["id"] != parent_workspace_id:
                if data["name"] == "child branch": 
                    branch_wid = data["id"]
                    num_of_child += 1  
            if num_of_child > 1: 
                raise Exception('There are multiple branches with same condition, fix!')               
        if num_of_child == 0:
            raise Exception('No branch found for this url, please recheck!')

        new_branch_url = f'https://cad.onshape.com/documents/{did}/w/{branch_wid}/e/{eid}'
        return new_branch_url

    def get_features(self, url):
        """
        Get the feature list of the part studio
        args: 
            url: onshape url of the design
        returns: 
            feats: a json dictionary with features as keys and feature ids as values
        """
        did, wid, eid, _ = self._url_elem(url) 
        
        url_ext = "/api/partstudios/d/did/w/wid/e/eid/features"
        fixed_url = self._build_url(url_ext, did, wid, eid) 

        headers = {
                "Accept": "application/json;charset=UTF-8; qs=0.09", 
                "Content-Type": "application/json"
            }
        params, payload = {}, {}
        method = "GET"
        response = self.client.api_client.request(method, url=self.base + fixed_url, 
                                                    query_params=params, 
                                                    headers=headers, 
                                                    body=payload)

        # response = response.json() 
        data = json.loads(response.data)   
        feats = {}
        for item in data['features']:
            feat_name = item['message']['name']
            feat_type = item['message']['featureType']
            feat_id = item['message']['featureId']
            feats[feat_name] = {'type': feat_type, 'id': feat_id} 
        return feats
    
    def delete_feature(self, url, feats, feat_to_delete): 
        """
        deletes features from Onshape url using feature name
        """
        did, wid, eid, _ = self._url_elem(url) 
        url_ext = "/api/partstudios/d/did/w/wid/e/eid"
        fixed_url = self._build_url(url_ext, did, wid, eid) 

        if len(feat_to_delete) == 0: 
            return 
        for feat_name in feat_to_delete: 
            if feat_name not in feats: 
                warnings.warn('feature to delete is not found in the provided feature data')
                continue 
            else:
                feat_id = feats[feat_name]['id']  # get feature id
                feat_url = self.base + fixed_url + f"/features/featureid/{feat_id}"
                method = "DELETE"
                headers={
                        "Accept": "application/json;charset=UTF-8; qs=0.09", 
                        "Content-Type": "application/json"
                    }
                params = {}
                payload = {
                        "feature": feat_id
                    }
                response = self.client.api_client.request(method, url=feat_url, 
                                                        query_params=params, 
                                                        headers=headers, 
                                                        body=payload)

    def copy_workspace(self, url):

        did, wid, eid, _ = self._url_elem(url)
        fixed_url = "/api/documents/did/workspaces/wid/copy"
        fixed_url = fixed_url.replace('did', did).replace('wid', wid)


        method = "POST"
        headers = { "Accept": "application/json;charset=UTF-8; qs=0.09", 
                    "Content-Type": "application/json"
                    }
        params = {}
        payload = { 
                    "newName": "newWorkSpace"
                }

        response = self.client.api_client.request(method, url=self.base + fixed_url, 
                                                query_params=params, 
                                                headers=headers, 
                                                body=payload)


        data = json.loads(response.data)
        try:
            new_did = json.dumps(data['newDocumentId'])[1:-1]
            new_wid = json.dumps(data['newWorkspaceId'])[1:-1]
            new_url = 'https://cad.onshape.com/documents/d/' + new_did + '/w/' + new_wid

        except KeyError:
            new_did = None
            new_wid = None
            new_url = None

        return new_url


    def get_featurescript(self, url):
        """
        Get the feature script of the part studio
        args: 
            url: onshape url of the design
        returns: 
            featscript: a json file of featurescript
        """
        did, wid, eid, _ = self._url_elem(url) 
        
        url_ext = "/api/partstudios/d/did/w/wid/e/eid/featurescript"
        fixed_url = self._build_url(url_ext, did, wid, eid) 

        headers = {
                "Accept": "application/json;charset=UTF-8; qs=0.09", 
                "Content-Type": "application/json"
            }
        params, payload = {}, {}
        method = "POST"
        response = self.client.api_client.request(method, url=self.base + fixed_url, 
                                                    query_params=params, 
                                                    headers=headers, 
                                                    body=payload)

        data = json.loads(response.data)   
        with open("featurescript.json", "w") as outfile:
            json.dump(data, outfile)

        return data


    def export_stl(self, url, filename):
        """
        args: 
            url: onshape document url, it must be in the following format 
            https://cad.onshape.com/api/partstudios/d/did/w/wid/e/eid 
            filename: name of the stl file to be saved e.g. 'Downloads/output.stl'

        returns: 
            saves stl file in the 'filename' location 

        """
        did, wid, eid, _ = self._url_elem(url)
        url_ext = '/api/partstudios/d/did/w/wid/e/eid/stl'
        method = 'GET'

        params = {}
        payload = {}
        headers = {'Accept': 'application/vnd.onshape.v1+octet-stream',
                    'Content-Type': 'application/json'}

        fixed_url = self._build_url(url_ext, did, wid, eid) 

        response = self.client.api_client.request(method, url=self.base + fixed_url, 
                                                    query_params=params, 
                                                    headers=headers, 
                                                    body=payload)

        with open(filename, 'wb') as f:
            f.write(response.data.encode())



    def export_step(self, url, filename):
        """
        export onshape url to step file (b-rep)
        """

        did, wid, eid, _ = self._url_elem(url)
        # first, get translation id from the request data
        parsed_data = self.createPartStudioTranslation(url, filename)

        if parsed_data:
    
            translation_url = parsed_data['href']
            url_list = translation_url.split("/")
            translation_id = url_list[-1]
            method = "GET"
            
            new_url = self.base + "/api/v2/translations/{}".format(translation_id)

            headers = {'Accept': 'application/vnd.onshape.v1+octet-stream',
                    'Content-Type': 'application/json'}

            # keep checking status of the request
            start_time = time.time()
            timeout = 60 # if step is not exported within 60 second we discard the url 
        
            while True:
                # second, use the translation id to check the translation status
                response = self.client.api_client.request(method, 
                        url=new_url,
                        query_params={}, 
                        headers={}, 
                        body={}
                    )
                response_data = json.loads(response.data) 
                state = response_data['requestState']   
                if state == "DONE":
                    break
                
                if time.time() - start_time >= timeout:
                    break 

            # extract external data id from the response
            try:
                external_data_id = response_data["resultExternalDataIds"][0]
                did = response_data["documentId"]
                step_url = "https://cad.onshape.com/api/documents/d/{}/externaldata/{}".format(did, external_data_id)

                # download the step file 
                step_method = 'GET'
                params, payload = {}, {}
                headers = {'Accept': 'application/vnd.onshape.v1+octet-stream',
                        'Content-Type': 'application/json'}
                response = self.client.api_client.request(step_method, url=step_url, query_params=params, headers=headers, body=payload)

                with open(filename, 'wb') as f:
                    f.write(response.data.encode())

            except:
                return 

        else: 
            return None