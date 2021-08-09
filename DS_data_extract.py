#dervied from common_images_only
import boto3
import csv
import json

import urllib.request

import pymysql
import sys
import os
import zipfile
import pyAesCrypt
from os import stat, remove
import shutil
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import itertools
import copy
from botocore.client import Config
REGION = 'us-east-2a'

rds_host = "padnetdbprod.cv910s0qh4yg.us-east-2.rds.amazonaws.com"
db_name = "padnetDBProd"
username = ""
password = ""
folder_path = ""

def get_secret():
    secret_name = "secretPADProdDB"
    region_name = "us-east-2"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print("-----------",str(e))
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
            #print("text_secret_data",text_secret_data)
            return text_secret_data
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            print("binary_secret_data",binary_secret_data)
    







def highpass_filter(data, BUTTER_ORDER=3, sampling_rate=200, cut_off=0.6):
    Wn = (float(cut_off) / (float(sampling_rate) / 2.0), 0.95)
    b, a = signal.butter(BUTTER_ORDER, Wn, 'pass')
    return signal.filtfilt(b, a, data)


def lowpass_filter(x, cutoff=4, fs=100, order=5):
    """
    low pass filters signal with Butterworth digital
    filter according to cutoff frequency

    filter uses Gustafsson’s method to make sure
    forward-backward filt == backward-forward filt

    Note that edge effects are expected

    Args:
        x      (array): signal data (numpy array)
        cutoff (float): cutoff frequency (Hz)
        fs       (int): sample rate (Hz)
        order    (int): order of filter (default 5)

    Returns:
        filtered (array): low pass filtered data
    """
    nyquist = fs / 2
    b, a = signal.butter(order, cutoff / nyquist)
    if not np.all(np.abs(np.roots(a)) < 1):
        raise PsolaError('Filter with cutoff at {} Hz is unstable given '
                         'sample frequency {} Hz'.format(cutoff, fs))
    filtered = signal.filtfilt(b, a, x, method='gust')
    return filtered


def lambda_handler(event):
    # TODO implement
    #print(event[:1])
    print(type(event))
    #event = json.loads(event['body'])
    #pid = event['padnet_data_id']
    padnet_id = event
    

   
    
    print(""" Select LEFT_FINGER_WAVEFORM,RIGHT_FINGER_WAVEFORM,LEFT_TOE_WAVEFORM,RIGHT_TOE_WAVEFORM from  PADNET_DATA Where Padnet_data_Id = """ + "'" + str(event) + "'")
    
    #conn= pymysql.connect(rds_host, user=uname, passwd=pswd, db="padnetDBProd", connect_timeout=5)
    conn= pymysql.connect("padnetdbprod.cv910s0qh4yg.us-east-2.rds.amazonaws.com", user="padacc", passwd="Padnet%747#Medix", db="padnetDBProd", connect_timeout=5)
    print("before with ")
    result = []
    with conn.cursor() as cur:
        cur.execute(
        """ Select LEFT_FINGER_WAVEFORM,RIGHT_FINGER_WAVEFORM,LEFT_TOE_WAVEFORM,RIGHT_TOE_WAVEFORM,
            Left_ABPI_Ref_Val, Right_ABPI_Ref_Val, Left_ABPI_Result, Right_ABPI_Result, Final_Result_Ref,DEVICE_ID
            from  PADNET_DATA Where Padnet_data_Id = """ + "'" + str(event) + "'"
            )
        
        desc = cur.description
        column_names = [col[0] for col in desc]

        #conn.commit()
        #cur.close()
        print("after  with ",cur)
        for row in cur:
            result.append(list(row))
        print(result[:9])
    

    resul2 = copy.deepcopy(result[0])  
    # print("  resul2 ",resul2[:9])
    res = {} 
    for key in column_names: 
        for value in resul2: 
            res[key] = value 
            resul2.remove(value) 
            break 


    if len(result) == 0:
        res['leftFingerWaveform'] = ""
        res['rightFingerWaveform'] = ""
        res['leftToeWaveform'] = ""
        res['rightToeWaveform'] = ""
        resp = {"lfw":"","rfw":"","ltw":"","rtw":"","data":json.dumps(res)}
        return {
        'statusCode': 200,
        'body': json.dumps(resp)
        }
        
    # print("post result")
    # print(len(result))
    # print(type(result))
    # print(result[0])
    # print(type(result[0][0]))
    
    lfw = result[0][0]
    rfw = result[0][1]
    ltw = result[0][2]
    rtw = result[0][3]
    device_id = result[0][9]

    # print(lfw)
    # print(rfw)
    # print(ltw)
    # print(rtw)
    
    #print("type --------",type(rfw))
    
    #print("======================os====listing tmp directory=======",device_id)
    #print(os.listdir("/tmp/"))

    lfw_garph_path = ""
    rfw_garph_path = ""
    ltw_garph_path = ""
    rtw_garph_path = ""
    lfw_image_name,rfw_image_name,ltw_image_name,rtw_image_name = "","","",""

    if len(lfw) > 2 :
        lfw_garph_path,lfw_image_name =  create_graph(lfw,"lfw",str(padnet_id),str(device_id))
    if len(rfw) > 2 :      
        rfw_garph_path,rfw_image_name =  create_graph(rfw,"rfw",str(padnet_id),str(device_id))
    if len(ltw) > 2 :      
        ltw_garph_path,ltw_image_name =  create_graph(ltw,"ltw",str(padnet_id),str(device_id))
    if len(rtw) > 2 :      
        rtw_garph_path,rtw_image_name =  create_graph(rtw,"rtw",str(padnet_id),str(device_id))

    
    #with open(os.getcwd()+"/"+ str(device_id) + "_" +  str(padnet_id) + "/" + str(device_id) + "_" +  str(padnet_id) +'.csv', 'w', newline='') as file:
    #    writer = csv.writer(file)
    #    writer.writerow(["SN", "LEFT_ABPI_REF_VAL", "RIGHT_ABPI_REF_VAL", "LEFT_ABPI_RESULT", "RIGHT_ABPI_RESULT", "FINAL_RESULT_REF"])
    #    writer.writerow([1, result[0][4],result[0][5],result[0][6],result[0][7],result[0][8]])

    padnet_id_string = str(padnet_id)

    



    complete_result = {"padnet_data_id":padnet_id,
                        "lfg":lfw_image_name,
                        "rfg":rfw_image_name,
                        "ltg":ltw_image_name,
                        "rtg":rtw_image_name
    }



    try:

        print("rtw_garph_path========",rtw_garph_path)
        print("lfw_image_name=============",lfw_image_name)
        global folder_path
        print("folder_path=============",folder_path)
    except Exception as e:
        d = "Exception-------------------->" + str(e) 
        print(d)   

    return complete_result
    

    
def create_graph(touch_segment,text,padnet_id,device_id):
    global folder_path

    padnet_data_id = str(padnet_id)
    sizezz = sys.getsizeof(touch_segment)
    l = len(touch_segment) 
    d = "textd-------------------->" + str(text) + "--------" + os.getcwd()
    if not os.path.isdir(os.getcwd()+"/"+ device_id + "_" + padnet_id + "/"):
        os.mkdir(os.getcwd()+"/"+ device_id + "_" +  padnet_id + "/")
    relative_path = os.getcwd()+"/"+ device_id + "_" +  padnet_id + "/"                  #/home/ec2-user/python_code/20200301056_27650/
    d = "relative_path-------------------->" +  "--------" + relative_path

    folder_path	= relative_path
    print(d)
 
    f = open(relative_path +  padnet_data_id+text+".zip","wb")
    z = json.loads(touch_segment)
    f.write(bytes(z))
    f.close()
    


   
    with zipfile.ZipFile(relative_path + padnet_data_id+text+".zip", 'r') as zip_ref :
        for name in zip_ref.namelist():
            print('%s'%(name))
        zip_ref.extractall(relative_path+"//")
    print("name--",name)                                                                #  20200729102545.txt.aes
    
    last_name = name
    file_name = name
    #all_files = os.listdir(relative_path+"home/biomedix/PADnet/Views/Padnet_Data/")
    #print("all_files--",all_files)
    #for x in all_files :
    #    if x == last_name :
    #        file_name = x
    aes_file_loc = relative_path + file_name[0:-7]+"aes"                           #/home/ec2-user/python_code/20200301056_27650/20200729102646.aes
    txt_file_loc = relative_path + file_name[0:-7]+"txt"
  
    #d = "all_files-------------------->" +  "--------" + str(all_files)
    #print(d)
    d = "file_name-------------------->" +  "--------" + file_name
    print(d)
    d = "aes_file_loc-------------------->" +  "--------" + aes_file_loc
    print(d)
    d = "txt_file_loc-------------------->" +  "--------" + txt_file_loc
    print(d)
    

    
    shutil.copy(relative_path+file_name,aes_file_loc) 

    
    bufferSize = 64 * 1024
    password = "PadNet@123"
    pyAesCrypt.decryptFile(aes_file_loc, txt_file_loc, password, bufferSize)
    

    with open(txt_file_loc,"r") as fo:
        plot_points = fo.read()

    d = "plot_points-------------------->" +  "--------" + str(plot_points[:30])
    print(d)
    if  len(plot_points) ==2 :
        d = "no plot_points-------------------->" +  "--------" + str(plot_points[:30])
        print(d)
        shutil.rmtree(relative_path)
        return "",""

    new_plot_points = plot_points[1:-1].split(',')


    new_new_plot_points = []
    for x in new_plot_points:
       new_new_plot_points.append(int(x)) 

    new_new_plot_points = lowpass_filter(highpass_filter(new_new_plot_points))


    fname = padnet_data_id + "_" + text + "_" + file_name[0:-7] + "png"
    fname_with_path =  relative_path + padnet_data_id + "_" + text + "_" + file_name[0:-7] + "png"
    plt.grid(which='major', linestyle='-', linewidth='1', color='grey')
    plt.ylim([-5000, 5000])
    plot_points = [(j / 5 )for i, j in enumerate(new_new_plot_points)]

    plot_points = plot_points[-1000:]
    plt.plot(plot_points,color=[0, 0, 1, 1],linewidth=3)

    fname_with_path =  relative_path + padnet_data_id + "_" + text + "_filename1" +"png"
    plt.savefig( fname_with_path)

    plt.clf()
    plt.cla()

    print("fname_with_path------------",fname_with_path)                         #/home/ec2-user/python_code/20200301056_27650/27650_rfw_20200729102505.png

    #print("new_new_plot_points----",new_new_plot_points[:50])
    #print(type(new_new_plot_points)) 
    #with open(txt_file_loc,"w") as fo:
    #   fo.write(str(new_new_plot_points))

    np.savetxt(txt_file_loc, new_new_plot_points)
    #os.remove(relative_path + file_name[0:-7] + "aes")
    #os.remove(relative_path + file_name[0:-7] + "txt")
    #os.remove(relative_path + file_name[0:-7] + "txt.aes")
    #os.remove(relative_path  + padnet_data_id + text + ".zip")  #20191201020_26378rfw.zip
    return fname_with_path,fname
   
   
    
#lambda_handler(26356)    
    
    
def main():
    conn= pymysql.connect("padnetdbprod.cv910s0qh4yg.us-east-2.rds.amazonaws.com", user="padacc", passwd="Padnet%747#Medix", db="padnetDBProd", connect_timeout=5)
    result = []
    with conn.cursor() as cur:
        cur.execute(
        """ SELECT PADNET_DATA_ID,LEFT_FINGER_GRAPH,RIGHT_FINGER_GRAPH,LEFT_TOE_GRAPH,RIGHT_TOE_GRAPH FROM PADNET_DATA WHERE PIN IN ('10114','94138','27732','82199')""")

        desc = cur.description
        column_names = [col[0] for col in desc]

        #conn.commit()
        ##cur.close()
        print("after  with ",cur)
        for row in cur:
            result.append(list(row))
            #result.append(row)
        print(result[:9])
    print("quistionable PADNET_DATA_ID---",result)
    j=0
    for x in result:
        #print("x--",x[0])
        print("calling for x===============",x[0])
        lambda_handler(x[0])
    #lambda_handler(28093)
    #lambda_handler(27937)
    #lambda_handler(27938)
    #lambda_handler(27939)




main()
