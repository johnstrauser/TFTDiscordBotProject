import os
import sys
import random
import discord
from discord.utils import get
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Result:
    def __init__(self, user=None, row=None, col=None):
        self.user = user
        self.row = row
        self.col = col

def apiQuery(username):
    return

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
    for i in range(len(rows)):
        sheet.update_cell(rows[i],col,(i+1))
    return 0

week = 1
week_col = 4 + (3 * (week - 1))
gamesPerWeek = 3
prevResults = []
token = 'NjE3MzkzMTI3NzQwOTMyMDk2.Xae0RQ.fNKQqUo62qFZkFjkoHfGvIIuhsE'

client = discord.Client()

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
            await message.channel.send("This is where I query the tft api... If there was one")
            #quuery tft api for results of match
            #list results will be the names of the players in order
            input = message.content[8:len(message.content)]
            #results = apiQuery(username)
            results = ['Travysty','August Rose','silentbluedeath','TGDerp','Elfire','Random','Gus','Strauscon']
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

