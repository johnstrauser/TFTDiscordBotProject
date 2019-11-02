import os
import sys
import random
import discord
from discord.utils import get
import gspread
import requests
import json
from oauth2client.service_account import ServiceAccountCredentials

class Result:
    def __init__(self, row=None, col=None):
        self.row = row
        self.col = col

def apiQuery(username):
    global api_key
    output = []
    #query api using username for puuid
    first_url = "https://na1.api.riotgames.com/tft/summoner/v1/summoners/by-name/" + username + "?api_key=" + api_key
    response = requests.get(first_url)
    if response.status_code != 200:
        return [1,response.status_code]
    init_puuid = response.json()["puuid"]
    
    #query api using puuid for match list
    second_url = "https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/"+ init_puuid +"/ids?api_key=" + api_key
    response = requests.get(second_url)
    if response.status_code != 200:
        return [2,response.status_code]
    match_id = response.json()[0]
    
    #using the match id get the participants puuids from the match
    third_url = "https://americas.api.riotgames.com/tft/match/v1/matches/"+ match_id +"?api_key=" + api_key
    response = requests.get(third_url)
    if response.status_code != 200:
        return [3,response.status_code]
    puuids = [1,2,3,4,5,6,7,8]
    for i in range(8):
        placement = response.json()["info"]["participants"][i]["placement"]
        id = response.json()["info"]["participants"][i]["puuid"]
        puuids[placement-1] = id
    
    #for each puuid, get the summoner name and add it to output
    for i in range(len(puuids)):
        fourth_url = "https://na1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/"+ puuids[i] +"?api_key="+ api_key
        response = requests.get(fourth_url)
        if response.status_code != 200:
            return [4+i,response.status_code]
        output.append(response.json()["name"])
        
    #return output
    return output

def getNameRows(names):
    global sheet
    out = []
    for i in range(len(names)):
        cell_list = sheet.findall(names[i])
        if len(cell_list) == 1:
            #name exists in a single location in the sheet
            out.append(cell_list[0].row)
        elif len(cell_list) > 1:
            #handle case where multiple of a name are found
            print("multiple of "+names[i]+" was found")
            out.append(-1)
        else:
            #name doesn't exist in the sheet
            loc = getUnknownLoc(names[i])
            if loc == -1:
                print('Unknown username space is full')
                exit()
            out.append(loc)
    return out

def getCols(rows):
    global sheet
    global gamesPerWeek
    global week_col
    output = []
    for i in range(len(rows)):
        for j in range(3):
            if sheet.cell(rows[i],week_col+j).value == '':
                output.append(week_col+j)
                break
        if i == len(output):
            print('At least one of the usernames entered has all of their games played for this week')
            return -1
    return output

def getUnknownLoc(name):
    global sheet
    global unknownsRow
    startRow = unknownsRow
    found = 0
    for i in range(20):
        val = sheet.cell(startRow+i,1).value
        if val == name:
            return startRow+i      
        elif val == '':
            sheet.update_cell(startRow+i,1,name)
            return startRow+i
    return -1

def updateCells(rows, col):
    global sheet
    global prevResults
    for i in range(len(rows)):
        sheet.update_cell(rows[i],col,(i+1))
        prevResults.append(Result(rows[i],col))
    return 0

week = 1
week_col = 4 + (3 * (week - 1))
gamesPerWeek = 3
prevResults = []
token = 'NjE3MzkzMTI3NzQwOTMyMDk2.XbtZSw.eLGR4WL5WuMkk1GaqnWoA96WxZY'

client = discord.Client()
api_key = "RGAPI-32b242a2-40c8-499c-ad9c-930512d1ab9d"
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('strausbot-test-10232260ea71.json',scope)
gspreadClient = gspread.authorize(creds)
sheet = gspreadClient.open("TEST").sheet1

temp_list = sheet.findall("Unknown names")
unknownsRow = temp_list[0].row


@client.event
async def on_ready():
    print(f'{client.user.name} has connected')

@client.event
async def on_message(message):
    global prevResults
    if message.author == client.user:
        return
    elif message.channel.name == 'tft-results':
        if message.content.startswith('!record'):
            #await message.channel.send("This is where I query the tft api... If there was one")
            #quuery tft api for results of match
            #list results will be the names of the players in order
            input = message.content[8:len(message.content)]
            results = apiQuery(input)
            if len(results) < 8:
                print("Query failed on #"+str(results[0])+" and the error code was "+str(results[1]))
            else:
                output = "Results from last game involving "+input+":\n"
                for i in range(len(results)):
                    output += str(i+1)+" - "+results[i]+"\n"
                output += "If this is not the correct results, enter '!undo' now."
                await message.channel.send(output)
            #return
            #query google doc for location of usernames
            #then check the 3 columns attributed to the week column
            prevResults = []
            #get where the usernames exist in the sheet
            #handle any unknowns in that function with a sub function
            rowsToAdd = getNameRows(results)
            #get the minimum valid column for each username
            #invalid = -1
            mins = getCols(rowsToAdd)
            if mins == -1:
                await message.channel.send("invalid recording")
                return
            #update all cells
            output = updateCells(rowsToAdd,max(mins))
            
            return 
        elif message.content.startswith('!undo'):
            if len(prevResults) != 0:
                for result in prevResults:
                    sheet.update_cell(result.row,result.col,"")
                prevResults = []
                await message.channel.send("Undo complete")
                return
            else:
                await message.channel.send("Nothing to undo")
                return
        elif message.content.startswith('!exit'):  
            if message.author.id != 134506172412723200:
                await message.channel.send("You do not have permission to use this command")
            else:
                await message.channel.send("Shutting down")
                exit()
        elif message.content.startswith('!test'):
            val = sheet.cell(3,3,value_render_option='FORMULA').value
            print(val)
    else:
        rand_list = [":too_real:",":thonk:",":spoink:",":monkaS:",":mamamia:",":madyoshi:",":kappa:",":drink:",":consider:",":chris:",":backinblack:",":officer:",":joy:",":money_mouth:",":stuck_out_tongue_winking_eye:",":rage:",":scream:",":mask:",":zzz:",":poop:",":smiling_imp:",":japanese_goblin:",":ghost:",":alien:",":sick:",":clown:",":eggplant:",":peach:",":free:",":wheelchair:",":flag_tw::hash::one:",":flag_eu:>:flag_us:",":regional_indicator_b::regional_indicator_i::regional_indicator_g::regional_indicator_p::regional_indicator_p:"]
        rand = random.random() * 100
        if rand > 95:
            await message.channel.send(random.choice(rand_list))
        
client.run(token)

