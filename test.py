import pymysql
import json
import os
# importing required modules
from zipfile import ZipFile

def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password = "root",
        db='mydb',
        )
    
    cur = conn.cursor()
    cur.execute("select @@version")
    output = cur.fetchall()
    print(output)    
    # To close the connection
    conn.close()    
   
     
    text= "Desktop"  
    
    touch_segment =  b'[80, 75, 3, 4, 20, 0, 0, 0, 8, 0, 11, 53, 115, 82, 137, 119, 116, 46]'
    print("NEW SEGMENT STARTED",text)
    f = open("/home/ec2-user/brajesh/temp/"+text+".zip","wb")       
    z = json.loads(touch_segment)     
    print("touch_segment data point :: ", z[2])     
    f.write(bytes(z))   
    f.close()
    
    
    print("======================os========after ===")
    print(os.listdir("/home/ec2-user/brajesh/temp"))
    print("======================os===========")
    
    # specifying the zip file name
    file_name = "/home/ec2-user/brajesh/temp/DesktopOk.zip"  
    # opening the zip file in READ mode
    with ZipFile(file_name, 'r') as zip_ref:
        for name in zip_ref.namelist():
            print('%s'%(name))
        zip_ref.extractall("/home/ec2-user/brajesh/temp")
        # printing all the contents of the zip file
        zip_ref.printdir()
      
        # extracting all the files
        print('Extracting all the files now...')
        #zip_ref.extractall()
        print('Done!')

# Driver Code
if __name__ == "__main__" :
    mysqlconnect()
