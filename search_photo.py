import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
ACCESS_KEY = "AKIA6RHHVSNYQLE2GsCUU"
SECRET_KEY = "6FK94Cl9r0IGisjZioiRH0SKykSZTrH7VZ+tKnpD" 
region = 'us-east-1'
es_service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, es_service, session_token=credentials.token)

def lambda_handler(event, context):
    print(event)
    # print(context)
    # TODO implement
    query = event['queryStringParameters']['q']
    print(query)
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName = 'PhotoBot',
        botAlias = '$LATEST',
        userId = 'id',
        sessionAttributes = {},
        requestAttributes = {},
        inputText = query
        )
    print(response)
    object1 = response['slots']['object']
    object2 = response['slots']['secondobject']
    print(object1)
    print(object2)
    
    
    photos_id = []
    tmp_result = []
    url = "https://vpc-photos-f36imjquajxkq35w4i5j6xxdee.us-east-1.es.amazonaws.com/photos/_search"
    
    if object1:
        es_query = {
            "query":{
                "match": {
                  "labels": object1
                }
            },
            "size": 3
        }
        res = json.loads(requests.get(url, headers={"Content-Type": "application/json"}, 
            auth=awsauth, data=json.dumps(es_query)).text)
    
        for item in res["hits"]["hits"]:
            photos_id.append(item["_source"]["objectKey"])
            tmp = {"url": "https://hw3b2.s3.amazonaws.com/"+str(item["_source"]["objectKey"]),
                    "labels": item["_source"]["labels"]
                }
            tmp_result.append(tmp)
    result = []
    if object2:
        es_query = {
            "query":{
                "match": {
                  "labels": object2
                }
            },
            "size": 3
        }
        res = json.loads(requests.get(url, headers={"Content-Type": "application/json"}, 
            auth=awsauth, data=json.dumps(es_query)).text)
    
        for item in res["hits"]["hits"]:
            photoname = item["_source"]["objectKey"]
            if photoname in photos_id:
                tmp = {"url": "https://hw3b2.s3.amazonaws.com/"+str(item["_source"]["objectKey"]),
                    "labels": item["_source"]["labels"]
                }
                result.append(tmp)
    else:
        result = tmp_result
                

    
    
    print(result)
    return {
        'statusCode': 200,
        'headers':{'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(result)
    }
