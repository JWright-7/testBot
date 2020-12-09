import discord
import random
import os
import re
from discord.ext import commands, tasks
from discord.utils import get
class moderation(commands.Cog):
    """Moderation Commands"""
    def __init__(self, client):
        self.client = client
        self.no_links_test = (540954170572931076, 735257858626682921, 735976817449631784)
        self.meeSix_test = self.client.get_user(159985870458322944)
        self.gifLink = r"https\:\/\/tenor\.com\/.*"
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation Loaded")
        
    @commands.command()
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=reason)
    
    @commands.command()
    async def clear(self, ctx, amount=2):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await member.kick(reason=reason)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Your Ping to the bot is: {round(self.client.latency * 1000)}ms')
    
    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
                return

    #moves links to the links channel if sent in a different channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if re.search(self.gifLink, message.content):
            return
        elif message.channel.id in self.no_links_test and re.search(self.url_regex, message.content):
            await message.delete()
            await message.author.send('Links are not allowed in that channel. I have moved it to the links channel for you.')
            target_channel_test = self.client.get_channel(698663294369792031)
            await target_channel_test.send(f'{message.author.mention} posted this link in another channel. I moved it here.\n \n {message.content}')
            print('A link has been moved.')

    #removes commands if used in the wrong channel
    @commands.Cog.listener()
    async def on_message(self, message):
        cmd_allowed = (735549676929155103, 735975828038484001, 548964988702949406, 692921076019232802)
        if message.content.startswith('.clear'):
            await self.client.process_commands(message)
        elif message.content.startswith('.') and message.channel.id not in cmd_allowed:
            await message.author.send('You cant use commands in that channel. Please use it in the commands channel.')
            await message.delete()
            print('Command was used in wrong channel')
        else:
            await self.client.process_commands(message)

    #Removes a message with a banned word, and warns the user who used the word.
    @commands.Cog.listener()
    async def on_message(self, message):
        with open('G:/Bots/testLavaLinkBot/bannedWords.txt', 'r') as wordCheck:
            wc = wordCheck.readlines()
            msgLst = message.content.split(' ')
            wordLst = []
            for words in wc:
                wrd = words.strip('\n')
                wordLst.append(wrd)
            x = 0
            while x < len(wordLst):
                if wordLst[x] in msgLst and message.author.id != 502165154105131028:
                    print('Banned Word Used')
                    await message.delete()
                    await message.author.send('This is a **warning**. You used a banned word, there are only 2 warnings. Use -wl to see a list of banned words. On the 3rd offense you get banned from the discord without warning.')
                    usrID = str(message.author.id)
                    with open('G:/Bots/testLavaLinkBot/warnedUsers.txt', 'a') as warned:
                        warned.write(f'{usrID}\n')
                    with open('G:/Bots/testLavaLinkBot/warnedUsers.txt', 'r') as warnedList:
                        wlFile = warnedList.readlines()
                        lst = []
                        for wlArray in wlFile:
                            wlIDs = wlArray.strip('\n')
                            lst.append(wlIDs)
                        if lst.count(usrID) == 3:
                            message.author.ban()
                            print('User has been banned for use of bad words 3 times.')
                        else:
                            await message.author.send(f'You currently have: {lst.count(usrID)} warning(s).')
                        return
                else:
                    x = x + 1
            await self.client.process_commands(message)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        goodbye = self.client.get_channel(474351822677475339)
        await goodbye.send(f'{member.mention} left the server.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome = self.client.get_channel(474351822677475339)
        await welcome.send(f'Welcome to the server {member.mention}')

    #Command error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send('An error has occured. I have sent the information to Hectic.')

        e = discord.Embed(
            title='An Error Occured.', 
            description=f'Error raised by {ctx.author}', 
            color=0x960505
        )
        e.add_field(name=str(type(error)), value=str(error))

        owner_id = self.client.get_user(235071908473733121)
        await owner_id.send(embed=e)
        raise error

    @commands.command()
    async def tmute(self, ctx, member:discord.Member = None):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='(╯°□°）╯︵ ┻━┻)')
        mRole = discord.utils.get(member.guild.roles, name='muted')
        if role in currentUser.roles or currentUser.id == 223906834988269569:
            if member is None:
                await ctx.send("Please enter a valid user.")
                return

            await member.add_roles(mRole)
            await ctx.send(f'{str(member)} has been muted.')
        else:
            await ctx.send("You dont have permission to use that command.")
        
    @commands.command()
    async def tunmute(self, ctx, member : discord.Member = None):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='(╯°□°）╯︵ ┻━┻)')
        mRole = discord.utils.get(member.guild.roles, name='muted')
        if role in currentUser.roles or currentUser.id == 223906834988269569:
            if member is None:
                await ctx.send("Please enter a valid user.")
                return
            await member.remove_roles(mRole)
            await ctx.send(f'{str(member)} Has been unmuted.')
        else:
            await ctx.send("You dont have permission to use that command.")

def setup(client):
    client.add_cog(moderation(client))