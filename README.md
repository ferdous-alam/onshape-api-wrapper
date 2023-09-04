# onshape-api-wrapper
This is a simple python wrapper to work with Onshape REST API via the onshape-client. 

# Installation 
Make sure to install onshape-client

    pip install onshape-client 

# Test 
There is a simple unittest provided in this repo. To run the unittest you will need the onshape api access key and api secret key. You can get these keys from onshape developer portal once you have an onshape account. This is free to get. 

# Supported features

Currently the following features are supported: 
    
1. get onshape document version id: `version_id = api.get_version(url)`  
2. create a new version from the main document: `new_version_id = api.create_version(url)`
3. create a new branch from an existing version: `new_branch_url = api.get_branch_url(url)`
4. get a dictionary of features for a design: `features = api.get_features(url)`
5. delete a feature from a design: `api.delete_feature(url, features, featture_to_delete)`
6. copy an existing design: `api.copy_workspace(url)`
7. export to stl: `api.export_stl(url, filename)` or `api.export_step(url, filename)`