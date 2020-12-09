import discord
import random
import os
from discord.ext import commands, tasks
from discord.utils import get

class memes(commands.Cog):
    """Meme Commands"""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Memes Loaded")
    
    @commands.command()
    async def baker(self, ctx):
        """'-baker'"""
        await ctx.send('Baker is a loud rage monster that watches videos and eats Doritos all with an open mic.')

    @commands.command()
    async def danny(self, ctx):
        """'-danny'"""
        await ctx.send('Danny is deaf and lives in a cave.')

    @commands.command()
    async def tommy(self, ctx):
        """'-tommy'"""
        responses = ["They're Fisters",
                    "Level 3 scope",
                    "Afganiskan",
                    "Don't worry i'd do you",
                    "You're not a four head, you're a pentahead",
                    "Gascaniskan",
                    "Should we conkalude on them?",
                    "Is a mach-47 good?",
                    "What's it called?",
                    "We're going to be pinced",
                    "Hello?",
                    "I have no meds",
                    "Thanks Tommy, Thanks Vagina",
                    "What's wrong with micers bake?",
                    "UnlawfuGamer",
                    "m1416",
                    "just some guy laying prone in a tank",
                    "Sorry we didn't get the jubble-U",
                    "You alright there jimmy? ... That's Zane AGAIN!",
                    "5 Figures 'Great so its less than 10,000'",
                    "It's not an ism its chemistry",
                    "I wanted to convulge on them",
                    "I was confused on what you were trying to mean"]
        await ctx.send(f'{random.choice(responses)}')

    @commands.command()
    async def map(self, ctx):
        """'-map'"""
        maps = ["Customs",
                "Reserv",
                "Interchange",
                "Shoreline",
                "Factory",
                "Woods",
                "Labs"]
        await ctx.send(f'{random.choice(maps)}')
        vChannel = ctx.message.author.voice.channel
        members = vChannel.members
        connected= []

        for member in members:
            connected.append(member.name)
        await ctx.send(f'{random.choice(connected)} was chosen for Veto.')

def setup(client):
    client.add_cog(memes(client))