import json
import boto3
import pymysql
import pandas as pd
from io import StringIO
import sys
import smtplib as s



def lambda_handler():
    
    print('Start lambda_handler method===========')  
    # To connect MySQL database    
    conn = pymysql.connect(host='127.0.0.1',user='root',password ='root',db='mydb',port=3306)     
    cur = conn.cursor()
    cur.execute("select @@version")
    output = cur.fetchall()
    print(output)    
    # To close the connection
    #conn.close()   
    print("Connection Ready !!!!")
        
    client =  boto3.client('s3')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('import-members')
    print("S3 Created !!!!")
    objects = client.list_objects_v2(Bucket=bucket.name)
    for obj in objects['Contents']:  
      s3Path = obj['Key'] 
      print("obj['Key']::=============", obj['Key'])
      #if '/processed/' in s3Path :
      #     print("/processed/ path :: ===========",s3Path)
      #     processedCopyFilePath = s3Path
      if '/tobeprocess/' in s3Path and s3Path.endswith('.csv') and s3Path != '':   
          print("--------------------------"+ obj['Key']+"------------------------")   
          s3_object = s3.Object(bucket_name='import-members', key=s3Path)    
          s3_data = StringIO(s3_object.get()['Body'].read().decode('utf-8'))             
          df = pd.read_csv(s3_data,delimiter=',')
          #print('Original DataFrame: \n', df)                   
          records  = df.values.tolist()
          #print("List Data :: ", records)         
          print("Source File Path :: ", s3Path ,"")
          #print("Destination Path :: ", processedCopyFilePath)
          filename = s3Path.split("/")[-1]
          groupFolder =  s3Path.split("/")[-3]
          print('File Name ::=======================',filename)
          print('Group Folder ::=======================',groupFolder)
          copy_source = {
              'Bucket': 'import-members',
              'Key': s3Path
          }
                                 
          bulk_insert_qry = ''' INSERT INTO sales values (%s, %s, %s) '''               
          # Execute the query
          cursor = conn.cursor()             
          success = cursor.executemany(bulk_insert_qry,records)
          print('\nBulk Rows iterated using executemany() : ')  
          conn.commit()             
          bucket.copy(copy_source, groupFolder+'/processed/'+filename)
          print('File Copied Successfully .....')  
          response = client.delete_object(
                  Bucket='import-members',
                  Key=s3Path
              )             
                  
   
  
if __name__ == "__main__":
    lambda_handler()    
    