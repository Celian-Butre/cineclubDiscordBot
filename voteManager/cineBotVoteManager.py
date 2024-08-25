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
cineclubGuild = None

def readFilmList():
    csvFilmsPath = str(os.path.dirname(programPath) + "/filmList.csv")
    with open(csvFilmsPath, mode='r', newline='') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]

def uploadNewFilmList(filmList):
    csvFilmsPath = str(os.path.dirname(programPath) + "/filmList.csv")
    with open(csvFilmsPath, mode='w', newline='') as file:
        writer = csv.writer(file)
        for entry in filmList:
            writer.writerow([entry])

def load_csv_to_matrix():
    file_path = str(os.path.dirname(programPath) + "/votesList.csv")
    matrix = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            matrix.append(row)
    return matrix

def save_matrix_to_csv(matrix):
    file_path = str(os.path.dirname(programPath) + "/votesList.csv")
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for row in matrix:
            writer.writerow(row)

def update_csv(filename, variable_name, new_value):
    # Read the existing CSV file and store the data in a list
    rows = []

    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            if row and row[0] == variable_name:
                # Update the value if the variable already exists
                rows.append([variable_name, new_value])
            else:
                rows.append(row)
    # Write the updated data back to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(rows)

def get_value_from_csv(filename, variable_name):
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        print("hi")
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            print("row")
            if row and row[0] == variable_name:
                print(row[1])
                return row[1]  # Return the value if the variable is found
    
@bot.event
async def on_ready():
    global cineclubGuild, roleMessage, roleMessageID
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    cineclubGuild = await bot.fetch_guild(cineclubGuildID)
    
@bot.command(name = "ajouteFilm")
async def ajouteFilm(ctx, *, film_name: str):
    if discord.utils.get(ctx.guild.roles, id=bureauRoleID) in ctx.author.roles:
        filmList = readFilmList()
        if film_name not in filmList:
            filmList.append(film_name)
            await ctx.send(str("J'ai rajouté " + film_name + " à la liste"))
        uploadNewFilmList(filmList)

@bot.command(name = "listeLesFilms")
async def listeLesFilms(ctx):
    filmList = readFilmList()
    print(filmList)
    message = "Les films passés au cinéclub sont :"
    for film in filmList:
        message += "\n\t" + film
    await ctx.send(message)

@bot.command(name = "note")
async def note(ctx, rating: float, *, movie_name: str):
    if rating <= 10 and rating >= 0 and rating % 1 == 0:
        filmList = readFilmList()
        votesMatrix = load_csv_to_matrix()
        if movie_name in filmList:
            alreadyVoted = False
            for x in votesMatrix:
                print(x)
                print(x[0])
                print(movie_name)
                print(x[2])
                print(ctx.author.id)
                if x[0] == movie_name and x[2] == str(ctx.author.id):
                    await ctx.send(str("Je change ton vote de " + x[1] + " à " + str(rating)))
                    x[1] = rating
                    alreadyVoted = True
                    break
            if not alreadyVoted:
                votesMatrix.append([movie_name, rating, ctx.author.id])
                await ctx.send("C'est noté.")
            save_matrix_to_csv(votesMatrix)
        else:
            await ctx.send("Ce film n'est pas passé au cinéclub")
    else :
        await ctx.send("La note doit être entre 0 et 10 et entier")

@bot.command(name = "afficherLesMoyennes")
async def afficherLesMoyennes(ctx):
    votesMatrix = load_csv_to_matrix()
    filmList = readFilmList()
    dictionnary = {filmList: [0, 0] for filmList in filmList} #numberOfVotes, sum
    for x in votesMatrix:
        dictionnary[x[0]][0] += 1
        dictionnary[x[0]][1] += int(x[1])
    message = "Voici la moyenne des notes attribuées aux films passés au cinéClub\n"
    for film in dictionnary:
        if dictionnary[film][0] != 0:
            message +=  str("\t**" + film + "** à une note moyenne de " + str(round(dictionnary[film][1]/dictionnary[film][0],1)) + ".\n")# + str(dictionnary[film][0]) + " personnes l'ont noté.\n")
        else : 
            message +=  str("\t**" + film + "** n'a pas encore été noté.\n")
    await ctx.send(message)

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