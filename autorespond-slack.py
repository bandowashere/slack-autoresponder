# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Slack Autoresponder                                                         #
# v. 20241002                                                                 #
#                                                                             #
# MIT License                                                                 #
# Copyright (c) 2024 /bandowashere                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



# import dependencies
import requests
import time
from datetime import datetime


  
# initialize variables
slackToken = ""  # populate with "User OAuth Token" (api.slack.com/apps/{your app id}/oauth)
headers = {"Authorization": f"Bearer {slackToken}"}
autoresponse = ""  # populate with your auto response. MUST be URL encoded (urlencoder.org)



# check authentication
print()
authTestEP = "https://slack.com/api/auth.test"  # authentication endpoint
authTestResponse = requests.get(authTestEP, headers = headers)
if authTestResponse.status_code == 200:
    result = authTestResponse.json()

    if result.get("ok"):
        print("Authentication successful.")
        print(f"User ID: {result["user_id"]}")
        print(f"User Name: {result["user"]}")

    else:
        print("Authentication failed.")
        print(f"Error: {result.get("error")}")
        print()
        exit()

else:
    print(f"Request failed with status code: {authTestResponse.status_code}")
    print()
    exit()
print()



# initialize endpoints and check for new messages every 60 seconds
listConversationsEP = "https://slack.com/api/conversations.list?types=im"  # endpoint for user's DMs
historyConversationsEP = "https://slack.com/api/conversations.history"  # conversations endpoint
postMessageEP = "https://slack.com/api/chat.postMessage"  # endpoint to post a message
while True:
    noMessageSent = True
    dmIDList = []
    currentTime = time.time()  # already in Unix time
    timestamp = datetime.now()
    output = ''

    # get user's latest DMs
    listConversationsResponse = requests.get(listConversationsEP, headers = headers)
    for i in listConversationsResponse.json()["channels"]:
        updated = float(i["updated"]) / 1000
        id = i["id"]
        dmIDList.append(id)

    # pull conversation history and send message
    for i in dmIDList:
        channelQuery = "?channel=" + i
        ep = historyConversationsEP + channelQuery
        historyConversationsResponse = requests.get(ep, headers = headers)

        # check if there are any messages
        try:
            messages = historyConversationsResponse.json()["messages"]


            if messages:
                newestMessageTimestamp = float(messages[0]["ts"])
                newestMessageUser = messages[0]["user"]

                # check if the latest message was less than 60 seconds old and make
                # sure the user isn't the autoresponder
                if currentTime - newestMessageTimestamp <= 60 and authTestResponse.json()["user_id"] != newestMessageUser:
                    # send autoresponse
                    postQuery = "?channel=" + i + "&text=" + autoresponse 
                    ep = postMessageEP + postQuery
                    postMessageResponse = requests.get(ep, headers = headers)
                    noMessageSent = False

        except KeyError as e:
            print(f"{timestamp} - {e}: No messages?\n")
            continue  # no messages?

        except requests.exceptions.JSONDecodeError as e:
            print(f"{timestamp} - Failed to decode JSON: {e}\n")
            continue 

    # output
    if noMessageSent:
        print(f"{timestamp} - No autoresponses.")
        output = f"{timestamp} - No autoresponses."
        print()

    else:
        print(f"{timestamp} - Autoresponses sent.")
        output = f"{timestamp} - Autoresponses sent."
        print()

    with open("slack-autoresponder-log.txt", "a") as f:
        f.write(output + '\n')

    # repeat every 60 seconds    
    time.sleep(60)
