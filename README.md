# Dog Temp Texter


This system is designed to connect to a wireless network and send texts to a user about a temperature sensor. The user can setup alerts that will send additional messenges.

1. Clone this repo,
2. Make sure Balena CLI is installed
	```
	#Install NVM
	curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
	#Install Node 8
	nvm install 8
	#Install Balena
	npm install balena-cli -g --production --unsafe-perm
	```
3. On the Balena.io website, download image to be written to MicroSD card
3. ensure your BalenaOS device is connected on your local network and is advertising as `resin.local`
4. run `resin local configure /dev/mmcblk0`
5. Push this code: `balena local push resin.local`

## Dependancies

1. Balena.io
	- [] Create an account
	- [] Create a new project
	- [] Navigate to this repo that you cloned
	- [] Run the ```git remote add balena gh_sako0938@git.balena-cloud.com:gh_sako0938/doggiesensor.git``` command from the top right corner of your Balena account and project.
	- [] Edit the python or other files and commit them to GitHub as usual. Then after ```git push origin master``` do ```git push balena master``` to upload code to device.
	- [] You can also do ```balena local``` commands, look up more about that in the Balena docs.
	- [] In the Balena project page, navigate to the Environment Variables tab, and create environments variables as shown in .resin-sync.yml

2. Twilio
	- [] Create an account
	- [] Create API credentials
	- [] Obtain Twilio Account SID
	- [] Obtain Twilio Auth Token
	- [] Click "All Products and Services" --> Manage Numbers
	- [] Obtain a free phone number to use

## Check the Remote Repositories Registered To Your Code Repo
1. Get current status:
```
git remote -v
```
2. Make sure that you have a Remote for "Balena"
3. In order to pull in new code from the master branch, make sure there is a remote called "Upstream"
4. Add Upstream to your repo: 
```
git remote add upstream git@github.com:sako0938/DogTempTexter.git
```

5. Merge in latest code: 
```
git merge upstream/master
```

## Uploading Code to Balena (The Slower Release/Git Way)
1. Stage, Commit, and Push New Changes To GitHub
```
git add -A
git commit -m "New changes"
git push origin master
```
2. Push latest code to Balena
```
git push balena master
```

## Uploading Code to Balena (The Faster Development/Balena Way)
1. Put device into Local Mode from the Balena Web UI.
2. Go into root directory of github project.
3. Push code and build on device: ```balena local push```

# Setting Alerts
Respond back to the text message with ```limit=75``` in order to start sending alert messages when the temperature reaches this point, 75 degrees F.