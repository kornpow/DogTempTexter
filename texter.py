from twilio.rest import Client
from datetime import datetime
import socket
from math import fsum
from time import sleep

import MyPyDHT

import threading

def ReadDHT22(BCMnum,buf_t,buf_h):
	# humidity = -1
	# temp = -1
	retry = 0
	max_retry = 10
	while retry < max_retry:
		try:
			humidity, temp = MyPyDHT.sensor_read(MyPyDHT.Sensor.DHT22, BCMnum)
			# print("DHT22 Alive: Received:\t Temp: %f\tHumidity:%f" %(temp,humidity) )
			
			temp = (temp * 1.8) + 32
			buf_t.pop(0)
			buf_h.pop(0)
			buf_t.append(round(temp, 2) ) 
			buf_h.append(round(humidity, 2) )
			average_h = round(fsum(buf_h) / len(buf_h), 2)
			average_t = round(fsum(buf_t) / len(buf_t), 2)
			return (average_h, average_t, round((average_t-32)/1.8,2) ) 

		except Exception as e:
			print(e)
			retry = retry + 1
			sleep(0.5)

	return (-1,-1,-1)

def SendTextMessage(mymessage):
	# Your Account Sid and Auth Token from twilio.com/console
	account_sid = 'AC418d083117870727526b01a66b6ffc5c'
	auth_token = '2a569c979685138c2c59a469c6629b47'
	client = Client(account_sid, auth_token)
	message = client.messages.create(
	                              from_='+17208097549',
	                              body=mymessage,
	                              to='+17203334371'
	                          )
	print(message.sid)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
local_ip_address = s.getsockname()[0]

temp_buff =  [0 for i in range(0,3)]
humid_buff =  [0 for i in range(0,3)]

SendTextMessage('Bootup @ IP '+ local_ip_address+  ' at:' + datetime.strftime(datetime.now(),"%I:%M:%S %p") )

while True:
	print("Still Alive!")
	th = ReadDHT22(17,temp_buff,humid_buff)
	sleep(0.5)
	th = ReadDHT22(17,temp_buff,humid_buff)
	sleep(0.5)
	th = ReadDHT22(17,temp_buff,humid_buff)
	sleep(0.5)
	print(th)
	temp = th[1]
	print(temp)
	tempc = th[2]
	SendTextMessage("Still Monitoring! " + datetime.strftime(datetime.now(),"%H:%M:%S") + \
		" Temp (C/F): " + str(tempc)+ "/" + str(temp) + \
		"\n" + str(temp_buff) )
	sleep(30)
	