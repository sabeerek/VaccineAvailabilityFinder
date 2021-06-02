# VaccineAvailabilityFinder
A script to check Covid vaccine availability in India. Script run based on interested pincodes of a user and notify the availability through Telegram group.


The script is designed to run for mutiple configuration(vaccine_data_v1.json),
A instance in a configuration can have it's own pincodes, Dose1 availabilty check, Dose2 availability check, Age Limit, Telegram botChatID, botToken etc.
Indian covid vaccine support age 45+ and 18+ as of now. 

An example of config instance is below.
"PerambraArea45Dose1":{
		"Dose1": true,
		"Dose2": false,
		"AgeLimit": 45,
		"Pincodes":[673525,673526,673532],
		"botChatID": "1111111",
		"groupChatID": "-12312",
		"botToken": "11111:abcdPs"
	}

Setting Up Telegram notifier:
- To run the script, one has to create a Telegram Bot, here is the steps to create a Telegram bot and retrive the token("botToken"), https://sendpulse.com/knowledge-base/chatbot/create-telegram-chatbot
- Once the bot is created, add it in the Telegram group as admin where you wish to recieve the notification when the vaccine is available.
- Now get the groups chat ID("groupChatID"), using the bot token, Here is the seteps for the same https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
