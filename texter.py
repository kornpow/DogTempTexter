from twilio.rest import Client
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
from datetime import datetime
import socket
from math import fsum
from time import sleep
import time

import MyPyDHT
import os
import threading

from flask import Flask
from flask import send_file 
from flask import render_template
from flask import redirect, url_for
from flask import jsonify
from flask import request
from time import sleep

import schedule

class DogTempSensor(object):
	def __init__(self):
		self.dht22_bcm = 17

		# Set this to true in order to text every minute an alert!
		self.alert = False
		self.limit = None
		self.floor = None
		time.tzset()

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
		local_ip_address = s.getsockname()[0]

		# Buffers and sensor data class variables
		self.temp_buff =  [0 for i in range(0,4)]
		self.humid_buff =  [0 for i in range(0,4)]
		self.clean_sensors = (0,0,0)
		current_time = datetime.strftime(datetime.now(),"%I:%M:%S %p")

		# Send send message on bootup with ip address, useful for sshing and pushing code
		bootup_msg = 'Bootup @ IP '+ local_ip_address+  ' at:' + current_time + "\n"
		bootup_msg = bootup_msg + "Reply: \n`disable` to stop alerts\n"
		bootup_msg = bootup_msg + "`limit=` to set upper limit alerts\n"
		bootup_msg = bootup_msg + "`floor=` to set lower floor alerts\n"
		self.SendTextMessage(bootup_msg)

		# Store resin environment variable as a class variable
		self.mins_per_text = int(os.environ["TEXT_FREQ"])

		# Set the number of minutes for the default text frequency as a resin environment variable
		schedule.every(self.mins_per_text).minutes.do(self.SendInfoMessage)
		# Every 30 seconds send alert message if an alert occurs
		schedule.every(30).seconds.do(self.SendAlertMessage)
		# Every 3 seconds check the temp and humidity sensors and update the buffer
		schedule.every(3).seconds.do(self.ReadTHSensor)
		print("Started Temp and Humidity Reader Thread")

		t1 = threading.Thread(target=self.t_flask_server, name="flask_server")
		t1.setDaemon(True)
		t1.start()
		print("Started web server!")

		t2 = threading.Thread(target=self.TimeScheduler, name="HeartBeatScheduler")
		t2.setDaemon(True)
		t2.start()
		print("Scheduler")

		sleep(15)
		self.SendInfoMessage()


	# THREAD: This is the heartbeat when it checks if any of the scheduled events should be run
	# *************************************
	def TimeScheduler(self):
		while True:
		    schedule.run_pending()
		    sleep(1)

	# THREAD: Run Web Server to receive text events webhooks
	# ******************************************************
	def t_flask_server(self):
		while True:
			try:
				app = Flask(__name__)
				app.add_url_rule('/',view_func=self.ResponseTextServer)
				app.add_url_rule('/update',view_func=self.UpdateSensorLimit)
				app.add_url_rule('/in-bound',view_func=self.InBoundMessageResponse, methods=['GET', 'POST'])
				app.run(host='0.0.0.0', port=80)
				
			except Exception as e:
				sleep(30)

	# THREAD: Read temp and humidity sensor
	# *************************************
	def ReadTHSensor(self):
		# Get package of humidity, tempf, and tempc
		self.clean_sensors = self.ReadDHT22()
		print("Clean Sensors Readings: %s,%s,%s" % self.clean_sensors)
		self.UpdateAlertStatus()


	def UpdateAlertStatus(self):
		# Decide if alert flag should be set
		f_or_c = 2
		if self.limit != None:
			if self.clean_sensors[f_or_c] >= self.limit:
				self.alert = True
			else:
				self.alert = False

		elif self.floor != None:
			if self.clean_sensors[f_or_c] <= self.floor:
				self.alert = True
			else:
				self.alert = False
		else:
			self.alert = False
			# Check whether to use celcius or fahrenheit
			
			# if os.environ["ALERT_LOCAL"] == "C":
			# 	f_or_c = 2
			# elif os.environ["ALERT_LOCAL"] == "F":
			# 	f_or_c = 1


	def getTextInvoice(num=os.environ["CONTACT_NUMBER"],msg='test',pay=False):
		url = 'https://lnsms.world/invoice'
		try:
			# Get payreq from lnsms.world
			r = requests.post(url, data={'number':num,'text':msg})
			# Send payment with LND
			if pay:
				sendPaymentByReq(r.text)
		except Exception as e:
			print(f'get or pay error: {e}')


	# Send current state over text message
	def SendInfoMessage(self):
		# while True:
		current_time = datetime.strftime(datetime.now(),"%I:%M:%S %p")
		# print(current_time)

		msg_text = "Still Monitoring! " + current_time		


		if self.alert == True:
			# Dont double text when alert is active
			return
		msg_text = msg_text + "\n(Tc):" + str(self.clean_sensors[2]) + "C"

		if self.limit != None:
			msg_text = msg_text + "\nCurrent Limit " + str(self.limit) + "C"
		if self.floor != None:
			msg_text = msg_text + "\nCurrent Floor " + str(self.floor) + "C"
	

		msg_text = msg_text + "\nThreads: " + str(threading.active_count() )
		
		print(msg_text)

		self.SendTextMessage(msg_text)

	# Send alert state over text message
	def SendAlertMessage(self):
		# while True:
		current_time = datetime.strftime(datetime.now(),"%I:%M:%S %p")
		# print(current_time)

		if self.alert == True:
			msg_text = "WARNING:\nAlert Status: " + str(self.alert)
			if self.limit != None:
				msg_text = msg_text + "\nCurrent Limit " + str(self.limit) + "C"
			if self.floor != None:
				msg_text = msg_text + "\nCurrent Floor " + str(self.floor) + "C"
			msg_text = msg_text + "\n(Tc):" + str(self.clean_sensors[2]) + \
			"\n" +  "Threads: " + str(threading.active_count() )
			self.SendTextMessage(msg_text)
			return
		
		print("No active alerts")




	# TWILIO: Send a text message using twilio
	# You need to configure these environment variables in the web console and in .resin-sync.yml
	def SendTextMessage(self,mymessage):
		# Your Account Sid and Auth Token from twilio.com/console
		account_sid = os.environ['TWILIO_ACCT_SID']
		auth_token = os.environ['TWILIO_AUTH_TOKEN']
		client = Client(account_sid, auth_token)
		message = client.messages.create(
		                              from_=os.environ["TWILIO_NUMBER"],
		                              body=mymessage,
		                              to=os.environ["CONTACT_NUMBER"]
		                          )
		print(message.sid)

	# Flask Routine: Serve Index Page
	def ResponseTextServer(self):
		return render_template('index.html', env=os.environ, dogwalker=self)

	# Flask Post? From Twilio?
	def UpdateSensorLimit(self):
		return render_template('twilio_response.html')

	# This is Flask function that Twilio calls with response data
	def InBoundMessageResponse(self):
		# Get text message body from POST request
		body = request.values.get('Body', None)
		print("Received Message: %s" % str(body) )

		# Craft Twilio Response
		response = MessagingResponse()
		message = Message()
		rstring = None

		if body == None:
			print("No Body!!! Error")
			return render_template('twilio_response.html')

		if body.lower().startswith("limit="):
			self.floor = None
			self.limit = int(body[len("limit="):] )
			rstring = "Setting Temp Limit to {0} degrees {1}".format(self.limit, os.environ["ALERT_LOCAL"])
		elif body.lower().startswith("floor="):
			self.limit = None
			self.floor = int(body[len("floor="):] )
			rstring = "Setting Temp Floor to {0} degrees {1}".format(self.floor, os.environ["ALERT_LOCAL"])
		elif body.lower().startswith("disable"):
			rstring = "Disabling Alerts!"
			self.limit = None
			self.floor = None
		else:
			rstring = "Respond with message starting with `limit=/floor=/stop`, to set an alert!"
		message.body(rstring)
		response.append(message)

		return str(response)


	# DHT22: Return clean sensor data (humidity, tempf, tempc )
	def ReadDHT22(self):
		# humidity = -1
		# temp = -1
		retry = 0
		max_retry = 10
		while retry < max_retry:
			try:
				humidity, temp = MyPyDHT.sensor_read(MyPyDHT.Sensor.DHT22, self.dht22_bcm)
				# print("DHT22 Alive: Received:\t Temp: %f\tHumidity:%f" %(temp,humidity) )
				
				temp = (temp * 1.8) + 32
				self.temp_buff.pop(0)
				self.humid_buff.pop(0)
				self.temp_buff.append(round(temp, 2) ) 
				self.humid_buff.append(round(humidity, 2) )
				average_h = round(fsum(self.humid_buff) / len(self.humid_buff), 2)
				average_t = round(fsum(self.temp_buff) / len(self.temp_buff), 2)
				return (average_h, average_t, round((average_t-32)/1.8,2) ) 

			except Exception as e:
				print(e)
				retry = retry + 1
				sleep(0.5)

		return (-1,-1,-1)		


if __name__ == '__main__':
	hi = DogTempSensor()

	while True:
		print("Still Running")
		print("H,T,Tc: %s", hi.clean_sensors )
		print(hi.temp_buff)
		print(hi.humid_buff)
		sleep(5)


		