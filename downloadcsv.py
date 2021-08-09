import json
import os
import boto3
import pandas as pd
import sys


srcFileName="data.csv"
def lambda_handler(event, context):
    
    print("Inside padnet-csv-files  Lambda ")
    print("Starting new session.")
    conn = S3Connection()
    my_bucket = conn.get_bucket("padnet-csv-files", validate=False)
    print("Bucket Identified")
    print(my_bucket)
    key = Key(my_bucket,srcFileName)
    key.open()
    print(key.read())
    conn.close()
       
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
