import json
import boto3
import datetime
import requests
from requests_aws4auth import AWS4Auth
ACCESS_KEY = "AKIA6RHHVSNYQLE2GsCUU"
SECRET_KEY = "6FK94Cl9r0IGisjZioiRH0SKykSZTrH7VZ+tKnpD" 
region = 'us-east-1'
es_service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, es_service, session_token=credentials.token)


def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    photo_name = event['Records'][0]['s3']['object']['key']
   
    reko = boto3.client('rekognition')
    print(bucket_name)
    print(photo_name)
    print(reko)
    
    response = reko.detect_labels(
         Image={'S3Object':{'Bucket':bucket_name,'Name':photo_name}},
         MaxLabels=10)
    
    # print(response)
    labels = response["Labels"]
    result = []
    for l in labels:
        result.append(l["Name"])
    print(result) 
    
    body = {"objectKey": photo_name, "bucket": bucket_name, 
        "createdTimestamp":str(datetime.datetime.now()),
        "labels": result
    }
    url = "https://vpc-photos-f36imjquajxkq35w4i5j6xxdee.us-east-1.es.amazonaws.com/photos/_doc"
    
    res = requests.post(url, auth=awsauth,
                        data = json.dumps(body),
                        headers = {"Content-Type": "application/json"})
    print(json.loads(res.text))
    
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
