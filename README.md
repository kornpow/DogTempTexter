# Dog Temp Texter


This system is designed to connect to a wireless network and send texts to a user about a temperature sensor. The user can setup alerts that will send additional messenges.

1. Clone this repo, 
2. Make sure resin CLI is install
3. ensure your resinOS device is connected on your local network and is advertising as `resin.local`
4. run `resin local configure /dev/mmcblk0`
5. Push this code: `resin local push resin.local`

## Dependancies

1. Resin.io
	- [] Create an account
	- [] Create a new project
	
2. Twilio
	- [] Create an account
	- [] Create API credentials
	- [] Obtain Twilio Account SID
	- [] Obtain Twilio Auth Token
	- [] Click "All Products and Services" --> Manage Numbers
	- [] Obtain a free phone number to use
