import re
import discord
from discord.colour import Colour
import lavalink
from discord.ext import commands
import math
import random

from lavalink.events import Event, TrackStartEvent
from lavalink.models import BasePlayer

url_rx = re.compile(r'https?://(?:www\.)?.+')
time_rx = re.compile('[0-9]+')


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        lavalink.add_event_hook(self.track_hook)
        lavalink.add_event_hook(self.song_stuck)
        lavalink.add_event_hook(self.new_song)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Music Loaded.')
        if not hasattr(self.client, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            self.client.lavalink = lavalink.Client(self.client.user.id)
            self.client.lavalink.add_node('''LAVALINK CONNECTION INFO''')  # Host, Port, Password, Region, Name
            self.client.add_listener(self.client.lavalink.voice_update_handler, 'on_socket_response')

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.client.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the client and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        """ This check ensures that the client and command author are in the same voicechannel. """
        player = self.client.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the client to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the client to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Join a voicechannel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the client to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def song_stuck(self, event):
        if isinstance(event, lavalink.events.TrackStuckEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
            print('Song was stuck, I left')

    async def new_song(self, event):
        if isinstance(event, lavalink.events.TrackStartEvent):
            nonHiddenVC = ('660969140621934611', '762446734538178590', '368205240773902346', )
            hiddenVC = ('514606611969343519')
            testVC = ('544944229709774858', '772907744277430272', '772907788191137904', '772190302290444348') 
            channel = self.client.get_channel(548964988702949406)
            hiddenChannel = self.client.get_channel(692921076019232802)
            test = self.client.get_channel(735549676929155103)
            
            randColour = random.randint(0, 0xffffff)
            embed = discord.Embed(
                    title='Now Playing:',
                    description=f'**[{event.player.current.title}]({event.player.current.uri})**',
                    colour=randColour
                )
            if event.player.channel_id in testVC:
                return await test.send(embed=embed)
            elif event.player.channel_id in nonHiddenVC:
                return await channel.send(embed=embed)
            elif event.player.channel_id in hiddenVC:
                return await hiddenChannel.send(embed=embed)
            else:
                return

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.client._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `client.shards[shard_id].ws` but that assumes
        # the client instance is an AutoShardedclient.
    
    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if query == ():
                return await ctx.send('You must put a song name or link. If you are trying to resume, user -pause again.')

            if not player.is_connected:
                if not ctx.author.voice or not ctx.author.voice.channel:
                    await ctx.send('Join a voice channel.')

                permissions = ctx.author.voice.channel.permissions_for(ctx.me)
                if not permissions.connect or not permissions.speak:
                    await ctx.send('I dont have permission to join or speak in that channel.')

            if not url_rx.match(query):
                query = f'ytsearch:{query}'

            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                return await ctx.send('Nothing found!')
            randColour = random.randint(0, 0xffffff)
            embed = discord.Embed(colour=randColour)

            # Valid loadTypes are:
            #   TRACK_LOADED    - single video/direct URL)
            #   PLAYLIST_LOADED - direct URL to playlist)
            #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
            #   NO_MATCHES      - query yielded no results
            #   LOAD_FAILED     - most likely, the video encountered an exception during loading.        
            
            if results['loadType'] == 'PLAYLIST_LOADED':
                tracks = results['tracks']

                for track in tracks:
                    # Add all of the tracks from the playlist to the queue.
                    player.add(requester=ctx.author.id, track=track)

                embed.title = 'Now Playing:'
                embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'

                await ctx.send(embed=embed)
            elif player.is_playing:
                track = results['tracks'][0]
                randColour = random.randint(0, 0xffffff)
                embed = discord.Embed(
                    title='Queued:',
                    description=f'[{track["info"]["title"]}]({track["info"]["uri"]})',
                    colour=randColour
                )

                track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
                player.add(requester=ctx.author.id, track=track)
                await ctx.send(embed=embed)

            else:
                track = results['tracks'][0]
                track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
                player.add(requester=ctx.author.id, track=track)

            if not player.is_playing:
                await player.set_volume(5)
                await player.play()
            
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_connected:
                return await ctx.send('Not connected.')

            if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
                return await ctx.send('You\'re not in my voicechannel!')

            player.queue.clear()
            await player.stop()

            await self.connect_to(ctx.guild.id, None)
            await ctx.send('Goodbye.')
            print('Left the voice channel.')
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')
    
    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int=1):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            print('Displaying Queue.')
            player = self.client.lavalink.player_manager.get(ctx.guild.id)
            if not player.is_playing:
                return await ctx.send('Nothing is playing and the queue is empty.')
            
            if not player.queue:
                return await ctx.send('There is nothing in the queue.')

            items_per_page = 10
            pages = math.ceil(len(player.queue) / items_per_page)
            start = (page - 1) * items_per_page
            end = start + items_per_page
            queue_list = ''

            for i, track in enumerate(player.queue[start:end], start=start):
                queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri})\n'
            randColour = random.randint(0, 0xffffff)
            embed = discord.Embed(
                title=f'Songs in Current Queue: {len(player.queue)}',
                description=f'{queue_list}\n',
                colour=randColour
            )
            embed.set_footer(text=f'Viewing Page: {page}/{pages}')
            
            await ctx.send(embed=embed)
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')
    
    @commands.command(aliases=['np'])
    async def now(self, ctx):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)
            song = 'Nothing'

            if player.current:
                pos = lavalink.utils.format_time(player.position)[3:]
                if player.current.stream:
                    dur = 'LIVE'
                else:
                    dur = lavalink.utils.format_time(player.current.duration)[3:]
                song = f'**[{player.current.title}]({player.current.uri})**\n({pos}/{dur})'
            
            randColour = random.randint(0, 0xffffff)
            embed = discord.Embed(
                title='Now Playing:',
                description=song,
                colour=randColour
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')
    
    @commands.command()
    async def skip(self, ctx):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)
            if not player.is_playing:
                return await ctx.send('Nothing is playing.')
            else:
                await player.skip()
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')
    
    @commands.command()
    async def pause(self, ctx):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_playing:
                return await ctx.send('Not playing anything.')
            
            if player.paused:
                await player.set_pause(False)
                await ctx.send('Resumed')
            else:
                await player.set_pause(True)
                await ctx.send('Paused')
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')
    
    @commands.command()
    async def cq(self, ctx):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not player.queue:
                return await ctx.send('Nothing in Queue.')
            else:
                player.queue.clear()
                await ctx.send('Queue has been cleared.')
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

    @commands.command(aliases=['v'])
    async def volume(self, ctx, volume: int=None):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not volume:
                return await ctx.send(f'{player.volume}')

            await player.set_volume(volume)
            await ctx.send(f'The volume is now: {player.volume}%')
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

    @commands.command()
    async def repeat(self, ctx):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_playing:
                return await ctx.send('Nothing is playing.')

            player.repeat = not player.repeat

            await ctx.send('`Repeat ' + ('enabled`' if player.repeat else 'disabled`'))
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

    @commands.command()
    async def shuffle(self, ctx):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_playing:
                return await ctx.send('There is nothing playing.')

            player.shuffle = not player.shuffle
            await ctx.send(f'`Shuffle ' + ('enabled`' if player.shuffle else 'disabled`'))
        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

    @commands.command()
    async def remove(self, ctx, index: int):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)
            
            if not player.queue:
                return await ctx.send('`Nothing Queued.`')

            if index > len(player.queue) or index < 1:
                return await ctx.send('Index has to be >=1 and <= the queue size')

            index = index - 1
            removed = player.queue.pop(index)

            await ctx.send('`Removed **' + removed.title + '** from the queue`')

        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

    @commands.command()
    async def seek(self, ctx, time):
        currentUser = ctx.author
        role = discord.utils.get(ctx.guild.roles, name='DJ')
        if role in currentUser.roles:
            player = self.client.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_playing:
                return await ctx.send('There is nothing playing.')
            
            pos = '+'
            if time.startswith('-'):
                pos = '-'
            
            seconds = time_rx.search(time)

            if not seconds:
                return await ctx.send('You need to specify the amount you want to skip in seconds')

            seconds = int(seconds.group()) * 1000
            if pos == '-':
                seconds = seconds * -1
        
            track_time = player.position + seconds

            await player.seek(track_time)
            await ctx.send(f'Moved track to: `{lavalink.utils.format_time(track_time)[3:]}`')


        else:
            await ctx.send('You dont have permission to use that command. Message an Admin for permission.')

def setup(client):
    client.add_cog(Music(client))