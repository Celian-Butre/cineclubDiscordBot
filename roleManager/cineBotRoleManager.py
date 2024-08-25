import os

import discord
from discord.ext import commands

import csv

from dotenv import load_dotenv
load_dotenv()

programPath = os.path.abspath(__file__)




TOKEN = os.getenv('TOKEN')
roleChannelID = int(os.getenv('roleChannelID'))
bureauRoleID = int(os.getenv('bureauRoleID'))
cineclubGuildID = int(os.getenv('cineclubGuildID'))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!",intents=intents)

#globals
roleList = None
cineclubGuild = None

roleMessageID = None 
roleMessage = None

class RoleList:
    def __init__(self):
        self.roles = []

    
    def append(self, role):
        self.roles.append(role)

    def getRoleFromEmoji(self, emoji):
        for role in self.roles:
            if role.emoji == emoji:
                return(role)

class Role:
    def __init__(self, name, emoji, description):
        global cineclubGuild
        self.name = name
        self.emoji = emoji
        self.description = description
        self.discordRole = discord.utils.get(cineclubGuild.roles, name=self.name)

    def __str__(self):
        return ("clickez sur " + self.emoji + "  pour obtenir le rôle " + str(self.name) + ", c'est " + self.description)


def makeRoleList():
    global roleList
    csvRolesPath = str(os.path.dirname(programPath) + "/listOfRoles.csv")

    roleList = RoleList()
    with open(csvRolesPath, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in data:
            roleList.append(Role(row[0], row[1], row[2]))

async def add_role(reaction, user):
    global roleList
    await user.add_roles(roleList.getRoleFromEmoji(reaction.emoji).discordRole)

async def remove_role(reaction, user):
    global roleList
    await user.remove_roles(roleList.getRoleFromEmoji(reaction.emoji).discordRole)

@bot.event
async def on_ready():
    global cineclubGuild, roleMessage, roleMessageID
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    cineclubGuild = await bot.fetch_guild(cineclubGuildID)
    makeRoleList()
    await bot.get_channel(roleChannelID).purge()
    await sendRoles()



async def sendRoles():
    global roleMessage
    roleChannel = bot.get_channel(roleChannelID)
    message = "\n".join([str(role) for role in roleList.roles])
    roleMessage = await roleChannel.send(message)
    for role in roleList.roles:
        await roleMessage.add_reaction(role.emoji)

@bot.command(name = "sendRoles")
async def sendRolesByMessage(ctx):
    global roleMessage
    makeRoleList()
    if discord.utils.get(ctx.guild.roles, id=bureauRoleID) in ctx.author.roles:
        sendRoles()

@bot.event
async def on_reaction_add(reaction, user):
    global roleMessage
    if reaction.message == roleMessage:
        if user != bot.user:
            await add_role(reaction, user)

@bot.event
async def on_reaction_remove(reaction, user):
    global roleMessage
    if reaction.message == roleMessage:
        if user != bot.user:
            await remove_role(reaction, user)


bot.run(TOKEN)