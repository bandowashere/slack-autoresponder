################################################################################
# Slack Autoresponder                                                          #
# v. 20240910                                                                  #
# @bandowashere                                                                #
#                                                                              #
# MIT License                                                                  #
# Copyright (c) 2024 Kevin Southwick                                           #
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



# initialize Slack endpoints
authTestEP = "https://slack.com/api/auth.test"  # authentication endpoint
listConversationsEP = "https://slack.com/api/conversations.list?types=im"  # endpoint for user's DMs
historyConversationsEP = "https://slack.com/api/conversations.history"  # conversations endpoint
postMessageEP = "https://slack.com/api/chat.postMessage"  # endpoint to post a message



#check auth
print()
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



# check for new messages every 60 seconds
while True:
    noMessageSent = True
    dmIDList = []
    currentTime = time.time()  # already in Unix time

    # get user's latest DMs
    listConversationsResponse = requests.get(listConversationsEP, headers = headers)
    for i in listConversationsResponse.json()["channels"]:
        updated = float(i["updated"]) / 1000
        id = i["id"]
        user = i["user"]
        if currentTime - updated <= 86400:
            dmIDList.append((id, updated, user))

    # check for any new DMs (messages) in the last minute
    for i in dmIDList:
        channel = i[0]
        channelQuery = "?channel=" + channel
        ep = historyConversationsEP + channelQuery
        historyConversationsResponse = requests.get(ep, headers = headers)
        messages = historyConversationsResponse.json()["messages"]

        if messages:
            for j in messages:
                ts = float(j["ts"])  # timestamp in Unix time
                user = j["user"]
                
                # check in the last 60 seconds and make sure the user isn't the autoresponder
                if currentTime - ts <= 60 and authTestResponse.json()["user_id"] != user:

                    # send autoresponse
                    postQuery = "?channel=" + channel + "&text=" + autoresponse 
                    ep = postMessageEP + postQuery
                    postMessageResponse = requests.get(ep, headers = headers)
                    noMessageSent = False
                    break  # only need to send one message per channel
    
    # output
    if noMessageSent:
        print("No autoresponses sent in the last 60 seconds.")
        print()
    else:
        print("Autoresponses were sent in the last 60 seconds.")
        print()

    # repeat every 60 seconds    
    time.sleep(60)