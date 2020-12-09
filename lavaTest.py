import discord
import os
from discord.ext import commands
import lavalink

intents = discord.Intents.all()
intents.presences = False

client = commands.Bot(
    intents = intents,
    command_prefix = '.',
    case_insensitive=True
)
client.remove_command('help')

@client.event
async def on_ready():
    print('lavalink bot ready.')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Developed By Hectic'))
    
    cmdChannel = client.get_channel(548964988702949406)
    e = discord.Embed(
        title= 'New features this bot update.',
        description= 'Shows the latest changes made to the bot.',
        colour = discord.Colour.orange()
    )

    e.add_field(name='----------------------------------------', 
    value='• New Music function, now streams instead of downloads song.', inline=False)
    e.add_field(name='----------------------------------------', 
    value='• Added -seek, used to seek through a song `x` amount of seconds', inline=False)
 
    #await cmdChannel.send(embed=e)

#loads specified cog
@client.command()
async def load(message, extention):
    owner_id = client.get_user(235071908473733121)
    if message.author.id == 235071908473733121:
        client.load_extension(f'cogs.{extention}')
        await owner_id.send(f'{extention} was loaded.')
    else:
        await message.channel.send(f'{message.author.mention} You can not use that command. It is only used by Hectic')

#unloads specified cog
@client.command()
async def unload(message, extention):
    owner_id = client.get_user(235071908473733121)
    if message.author.id == 235071908473733121:
        client.unload_extension(f'cogs.{extention}')
        await owner_id.send(f'{extention} was unloaded.')
    else:
        await message.channel.send(f'{message.author.mention} You can not use that command. It is only used by Hectic')

#reloads specified cog
@client.command()
async def reload(message, extention):
    owner_id = client.get_user(235071908473733121)
    if message.author.id == 235071908473733121:
        client.unload_extension(f'cogs.{extention}')
        client.load_extension(f'cogs.{extention}')
        print(f'{extention} was reloaded.')
        await owner_id.send(f'{extention} was reloaded.')
    else:
        await message.channel.send(f'{message.author.mention} You can not use that command. It is only used by Hectic')

#sends feature requests to Hectic
@client.command()
async def request(ctx, *requestMessage: str):
    requestMessage = ' '.join(requestMessage)
    notif = discord.Embed(title='Command Request Recieved.', description='Your request is sent to Hectic to be put into the bot.', color=0x960505)
    notif.add_field(name='Request Recieved', value=f'{requestMessage}')
    await ctx.send(embed=notif)
    
    req = discord.Embed(titel='Command Request', color=0x960505)
    req.add_field(name=f'Requested by: {ctx.author}', value=f'{requestMessage}')

    owner_id = client.get_user(235071908473733121)
    await owner_id.send(embed=req)

#Command to show newest changes.
@client.command()
async def new(ctx):
    e = discord.Embed(
        title= 'New features this bot update.',
        description= 'Shows the latest changes made to the bot.',
        colour = discord.Colour.orange()
    )

    e.add_field(name='----------------------------------------', 
    value='• Changed now playing message to be a custom embed', inline=False)
    e.add_field(name='----------------------------------------', 
    value='• Changed Now playing message for queued songs to now be an Embed.', inline=False)
    e.add_field(name='----------------------------------------', 
    value='• Changed the queued song message to be an Embed with the user who added it.', inline=False)
    #e.add_field(name='----------------------------------------', 
    #value='• Added Welcome and Goodbye messages for when people join or leave the server.', inline=False)
    await ctx.send(embed=e)

#Among Us Rules
@client.command()
async def amg(ctx):
    embed = discord.Embed(
        title = 'Among Us Rules',
        description = 'These are the rules that we play by in this discord',
        colour = discord.Colour.orange()
    )

    embed.add_field(name='1.', value='During play **ALL** Mics are to be muted. Only unmute during **Meetings**.', inline=False)
    embed.add_field(name='2.', value='If killed, you can **NOT** speak until the game has been completed, you can use text chat however.', inline=False)
    embed.add_field(name='3.', value='Have fun, Dont be an idiot.', inline=False)
    await ctx.send(embed=embed)

#Among Us Settings
@client.command()
async def aset(ctx):
    embed = discord.Embed(
        title='Optimal Among Us Settings',
        description = 'Use these settings for the most fun',
        colour=discord.Colour.orange()
    )

    embed.add_field(name='Imposters', value='2 (lobby of 10), 1 (lobby < 10)', inline=False)
    embed.add_field(name='Confirm Ejects', value='Confirm Ejects = Off', inline=False)
    embed.add_field(name='Emergency Meetings', value='1', inline=False)
    embed.add_field(name='Emergency Cooldown', value='15s', inline=False)
    embed.add_field(name='Discussion Time', value='15s', inline=False)
    embed.add_field(name='Voting Time', value='120s', inline=False)
    embed.add_field(name='Player Speed', value='1x', inline=False)
    embed.add_field(name='Crewmate Vision', value='0.75x', inline=False)
    embed.add_field(name='Imposter Vision', value='1.5x', inline=False)
    embed.add_field(name='Kill Cooldown', value='22.5s', inline=False)
    embed.add_field(name='Kill Distance', value='Short', inline=False)
    embed.add_field(name='Visual Tasks', value='Off', inline=False)
    embed.add_field(name='Common Tasks', value='2', inline=False)
    embed.add_field(name='Long Tasks', value='2', inline=False)
    embed.add_field(name='Short Tasks', value='5', inline=False)

    await ctx.send(embed=embed)

#Bans a desired word
@client.command()
async def bw(ctx, word):
    currentUser = ctx.author
    role = discord.utils.get(ctx.guild.roles, name='(╯°□°）╯︵ ┻━┻)')
    if role in currentUser.roles:
        with open('G:/Bots/testLavaLinkBot/bannedWords.txt', 'a') as bannedWords:
            bannedWords.writelines(f'{word}\n')
            print(f'{word} has been added to the list')
            await ctx.send(f'{word} has been added to the list')
    else:
        await ctx.send('You dont have the right role to use this command.')

#Shows list of banned words
@client.command()
async def wl(ctx):
    with open('G:/Bots/testLavaLinkBot/bannedWords.txt', 'r') as readWords:
        bwl = readWords.readlines()
        print('wl has been requested.')
        embed = discord.Embed(
            title = 'Banned Word List',
            description = 'A list of banned words in this server.',
            colour = discord.Colour.orange()
        )
        for words in bwl:
            embed.add_field(name='\u200b', value=f'• **{words}**', inline=False)
        await ctx.send(embed=embed)
        return

#Clears the banned words list
@client.command()
async def cwl(ctx):
    currentUser = ctx.author
    role = discord.utils.get(ctx.guild.roles, name='(╯°□°）╯︵ ┻━┻)')
    if role in currentUser.roles:
        with open('G:/Bots/testLavaLinkBot/bannedWords.txt', 'w') as clearwl:
            listClear = clearwl.writelines('')
            print('list is clear')
    else:
        await ctx.send('You dont have the right role to use this command.')

#Clears the warning for each person
@client.command()
async def cwarn(ctx):
    currentUser = ctx.author
    role = discord.utils.get(ctx.guild.roles, name='(╯°□°）╯︵ ┻━┻)')
    if role in currentUser.roles or currentUser.id == 223906834988269569:
        with open('G:/Bots/TestBot/warnedUsers.txt', 'w') as cwarn:
            listClear = cwarn.writelines('')
            print('list is clear')
            await ctx.send('You have cleared the warning list. All users warning are now at 0')
    else:
        await ctx.send('You dont have the right role to use this command.')

#mutes all people in the voice channel of the person who used the command
@client.command()
async def mute(ctx):
    vChannel = ctx.author.voice.channel
    for member in vChannel.members:
        await member.edit(mute=True)

#Unmutes all people in the voice channel that was muted
@client.command()
async def unmute(ctx):
    vChannel = ctx.author.voice.channels
    for member in vChannel:
        await member.edit(mute=False)

#custom help command
@client.command()
async def help(ctx, *page):
    if page[0] == 'music' or page == ():
        e = discord.Embed(
            title= 'Command Help',
            description= 'Help for all commands.',
            colour = discord.Colour.orange()
        )

        e.add_field(name='`-play`', value= 'Used to play music, queue new songs or resume pause songs.\n Proper Use: `-play <URL or song name>`', inline=False)
        e.add_field(name='`-stop`', value='Used to stop the bot from playing, will also disconnect bot and clear the queue.\n Proper Use: `-stop`', inline=False)
        e.add_field(name='`-skip`', value='Used to skip the currently playing song and start the next in queue.\n Proper Use: `-skip`', inline=False)
        e.add_field(name='`-volume`', value='Used to change the volume of the bots music. \n Proper Use: `-volume <1-100>`', inline=False)
        e.add_field(name='`-cq`', value='Used to check the status of the queue.\n Proper Use: `-cq`', inline=False)
        e.add_field(name='`-qclear`', value='Used to clear the songs from the current queue. \n Proper Use: `-qclear`', inline=False)
        e.add_field(name='`-seek`', value='Used to change time in the song thats playing. \n Proper Use: `-seek <x amount of seconds>`', inline=False)
        e.add_field(name='`-now`', value='Used to show the song currently playing and how much time is left. \n Proper Use: `-now`', inline=False)
        e.set_footer(text='Music, -help mod or -help memes')

        await ctx.send(embed=e)
    elif page[0] == 'mod':
        em = discord.Embed(
            title='Moderation Help',
            description='Help for all the Moderation commands.',
            colour= discord.Colour.orange()
        )

        em.add_field(name='`-ban`', value='Used to ban a user in the discord.\n Proper Use: `-ban <user> <reason>`', inline=False)
        em.add_field(name='`-kick`', value='Used to kick a user from the discord.\n Proper Use: `-kick <user> <reason>`', inline=False)
        em.add_field(name='`-clear`', value='Used to clear messages in chat.\n Proper Use: `-clear <number of messages(max of 200)>`', inline=False)
        em.add_field(name='`-ping`', value='Used to show the ping to the discord server.\n Proper Use: `-ping`', inline=False)
        em.add_field(name='`-unban`', value='Used to unban a user from the discord.\n Proper Use: `-unban <user>`', inline=False)
        em.add_field(name='`-new`', value='Used to see what new features have been added. \n Proper Use: `-new`', inline=False)
        em.add_field(name='`-tmute`', value='Used to give someone the muted role not allowing any text chat \n Proper Use: `-tmute <@ user>`', inline=False)
        em.add_field(name='`-tunmute`', value='Used to see what new features have been added. \n Proper Use: `-tunmute <@ user>`', inline=False)
        em.add_field(name='`-mute`', value='Used to mute everyone in the voice channel. \n Proper Use: `-nmute`', inline=False)
        em.add_field(name='`-unmute`', value='Used to unmute everyone in the voice channel. \n Proper Use: `-unmute`', inline=False)
        em.add_field(name='`-bw`', value='Used to add a word to the banned word list \n Proper Use: `-bw <word>`', inline=False)
        em.add_field(name='`-wl`', value='Used to show what words are in the banned word list. \n Proper Use: `-wl`', inline=False)
        em.add_field(name='`-cwl`', value='Used to clear the banned word list. \n Proper Use: `-cwl`', inline=False)
        em.add_field(name='`-cwarn`', value='Used to clear the warned list. \n Proper Use: `-cwarn`', inline=False)
        em.add_field(name='`-tunmute`', value='Used to see what new features have been added. \n Proper Use: `-tunmute <@ user>`', inline=False)
        em.set_footer(text='Moderation, -help music or -help memes')

        await ctx.send(embed=em)
    elif page[0] == 'memes':
        emb = discord.Embed(
            title='Memes Help',
            description='Help for all the meme commands',
            colour=discord.Colour.orange()
        )

        emb.add_field(name='`-baker`', value='Used to display the truth about Baker.\n Proper Use: `-baker`', inline=False)
        emb.add_field(name='`-danny`', value='Used to display the truth about Danny.\n Proper Use: `-danny`', inline=False)
        emb.add_field(name='`-tommyism`', value='Used to display a random quote from one of the Tommies.\n Proper Use: `-tommyism`', inline=False)
        emb.set_footer(text='Memes, -help music or -help mod')

        await ctx.send(embed=emb)
    elif page[0] == 'games':
        embe = discord.Embed(
            title='Game Commands',
            description='Help for all commands related to games',
            colour=discord.Colour.orange()
        )

        embe.add_field(name='`-amg`', value='Used to show the among us rules we play by. \n Proper Use: `-amg`', inline=False)
        embe.add_field(name='`-aset`', value='Used to show the among us settings we use. \n Proper Use: `-aset`', inline=False)
        embe.add_field(name='`-map`', value='Used to select a map and veto person for Tarkov. \n Proper Use: `-map`', inline=False)
        await ctx.send(embed=embe)
    else:
        await ctx.send('You must use -help music, -help mod or -help memes.')

for filename in os.listdir('G:\\Bots\\testLavaLinkBot\\cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run('''TOKEN GOES HERE''')