from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
import uuid
from threading import Thread
import threading
import time
from datetime import datetime
import random
import sys
import json
import multiprocessing as mp
class SendDeviceToCloudMessage():
    #Id,Fruit1,Percent1,Fruit2,Percent2,Fruit3,Percent3,ValidationBoolean

 

    def iothub_client_send_telemetry(self,client, photoId,fruit1,percent1,fruit2,percent2,fruit3,percent3,validationBoolean,feedback):
        '''def iothub_client_init(connection_string):
            # Create an IoT Hub client
            client = IoTHubDeviceClient.create_from_connection_string(connection_string)
            return client'''
        
        try:
            #client = iothub_client_init(connection_string)
            print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

 

            # Build the message with simulated telemetry values.

 

#            MSG_TXT = '{{"photoId":{photoId},"fruit1": {fruit1}, "percent1":{percent1}, "fruit2":{fruit2}, "percent2":{percent2}, "fruit3":{fruit3}, "percent3":{percent3}, "validationBoolean":{validationBoolean}}}'

 

#           msg_txt_formatted = MSG_TXT.format(photoId=photoId,fruit1=fruit1,percent1=percent1,fruit2=fruit2,percent2=percent2,fruit3=fruit3,percent3=percent3,validationBoolean=validationBoolean)
            ini_string = {"photoId":str(photoId),"fruit1": str(fruit1), "percent1":float(percent1), "fruit2":str(fruit2),"percent2":float(percent2), "fruit3":str(fruit3), "percent3":float(percent3), "validationBoolean":int(validationBoolean),"feedback":str(feedback)} 
 
            # printing initial json 
            msg_txt_formatted = json.dumps(ini_string)
           
            message = Message(msg_txt_formatted)

 


            # Send the message.
            print( "Sending message: {}".format(message) )
            client.send_message(message)
            print ( "Message successfully sent" )
            time.sleep(1)
            client.disconnect()

 

           
        except Exception as e:
            print("print error: ",e)