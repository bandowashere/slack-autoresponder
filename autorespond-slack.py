################################################################################
# Slack Autoresponder                                                          #
# v. 20240911                                                                  #
#                                                                              #
# MIT License                                                                  #
# Copyright (c) 2024 /bandowashere                                             #
#                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy #
# of this software and associated documentation files (the "Software"), to     #
# deal in the Software without restriction, including without limitation the   #
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or  #
# sell copies of the Software, and to permit persons to whom the Software is   #
# furnished to do so, subject to the following two conditions:                 #
# 1.) The above copyright notice and this permission notice shall be included  #
#     in all copies or substantial portions of the Software.                   #
# 2.) THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS  #
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF               #
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.   #
#     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY     #
#     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,     #
#     TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE        #
#     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                   #
# ##############################################################################



# import dependencies
import requests
import time


  
# initialize variables
slackToken = ""  # populate with "User OAuth Token" (api.slack.com/apps/{your app id}/oauth)
headers = {"Authorization": f"Bearer {slackToken}"}
autoresponse = ""  # populate with your auto response. MUST be URL encoded (urlencoder.org)



#check authentication
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
    
    # output
    if noMessageSent:
        print("No autoresponses sent in the last 60 seconds.")
        print()
    else:
        print("Autoresponses were sent in the last 60 seconds.")
        print()

    # repeat every 60 seconds    
    time.sleep(60)
