from discord.ext import commands, tasks
import discord
import time
import asyncio
import responses
import gameclasses

TOKEN = "MTE3NDM2ODY4OTUzODIyMDA5Mw.G4rucw.EQiTZrDt9-ABVxgtjJOH3ojxpwKfDn9gWhH3jY"
MAX_SESSION_TIME_MINUTES = 1
session = gameclasses.Session()
user_manager = gameclasses.UserManager()

async def send_message(ctx, user_message):
    try:
        response = responses.handle_response(user_message)
        await ctx.channel.send(response)
    except Exception as e:
        print("Error occured: ", e)

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    bot = commands.Bot(command_prefix='!', intents=intents)


    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running!")


    @bot.event
    async def on_message(ctx):
        # Make sure you are talking to someone else
        if ctx.author == bot.user:
            return
        
        # respond start with prefix
        if ctx.content.startswith(bot.command_prefix):
            command_exception_to_whitespace = ['list', 'add', 'update', 'del']
            command_name = ctx.content.split(' ')[0][1:]    # extract command name only
            if not bot.get_command(command_name):
                await send_message(ctx, ctx.content)
                return
            
            if any(command in ctx.content for command in command_exception_to_whitespace) or len(ctx.content.split(' ')) == 1:
                await bot.process_commands(ctx)
                return
            else:
                await send_message(ctx, ctx.content)
                return
        
        username = str(ctx.author)
        channel = str(ctx.channel)     
        if isinstance(ctx.channel, discord.TextChannel):
            if bot.user.mention in ctx.content:
                user_message = str(ctx.content.replace(f'<@{str(bot.user.id)}>', '').strip())
                await send_message(ctx, user_message)
        elif isinstance(ctx.channel, discord.DMChannel):
            if bot.user.mention in ctx.content:
                user_message = str(ctx.content.replace(f'<@{str(bot.user.id)}>', '').strip())
            else:    
                user_message = str(ctx.content)
            await send_message(ctx, user_message)


    # loop every given minutes
    @tasks.loop(seconds=5)
    async def update_game_activity():
        if session.get_game_session_status:
            if time.time() - session.last_activity_time > MAX_SESSION_TIME_MINUTES * 60:
                await session.channel.send(responses.game_terminated_message())
                session.set_no_game_session()
                user_manager.default_user()
                update_game_activity.stop()


    @bot.command(name='command')
    async def help_bot_commands(ctx):
        await ctx.channel.send(responses.list_command())


    @bot.command(name='instr')
    async def game_instruction(ctx):
        await ctx.channel.send(responses.game_instruction())


    @bot.command(name='join')
    async def join_game(ctx):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.5)
            await ctx.channel.send(responses.game_instruction())
            return

        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command

        if user_manager.check_user(user.id, user.name):
            await ctx.reply(responses.already_joined_message())
            return
        elif not session.player_accept:
            await ctx.reply("Cannot join the game. " + responses.game_channel_message(ctx.channel))
            return
        
        status = user_manager.add_user(user.id, user.name)
        if status:
            await ctx.reply(f"**@{user.name}** join the game")

        embed = discord.Embed(title="List of Players", color=discord.Color.blurple())
        for i, (user_id, user_data) in enumerate(user_manager.users.items(), start=1):
            embed.add_field(name=f"{i}. {user_data['username']}", value="", inline=False)

        view = gameclasses.StartGame(user_manager, ctx.channel, session)
        await ctx.channel.send(embed=embed, view=view)


    @bot.command(name='start')
    async def start_game(ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if session.game_started:
            await ctx.channel.send(responses.game_channel_message(session.channel))
            return
        
        update_game_activity.start()
        session.set_game_session_status(bot.get_channel(ctx.channel.id))
        await ctx.channel.send(responses.game_start_message())
        await asyncio.sleep(0.5)
        await ctx.channel.send(responses.game_instruction())

    
    @bot.command(name='stop')
    async def stop_game(ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            return
        
        if session.channel == ctx.channel:
            update_game_activity.stop()
            session.set_no_game_session()
            await ctx.channel.send(responses.game_stop_message())
        else:
            await ctx.channel.send(responses.not_game_channel_message(session.channel))


    @bot.command(name='list')
    async def get_food_list(ctx, *, food_list=None):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.5)
            await ctx.channel.send(responses.game_instruction())
            return
        
        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return

        if not user_manager.check_user(user.id, user.name):
            await ctx.reply(responses.not_registed_message())
            return
        
        if not food_list:
            await ctx.reply(responses.list_empty_message())
            return

        food_items = [food_item.strip() for food_item in food_list.split(',')]
        embed = discord.Embed(title="Food List", color=discord.Color.green())
        for i, item in enumerate(food_items, start=1):
            embed.add_field(name=f"{i}. {item}", value="", inline=False)
        view = gameclasses.ListMenu(user_manager, bot, food_items)
        await ctx.reply(embed=embed, view=view)
        await ctx.channel.send(responses.list_edit_message())


    @bot.command(name='vote')
    async def vote_ranking(ctx, *, ranking_list=None):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.5)
            await ctx.channel.send(responses.game_instruction())
            return
        
        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.channel.send(responses.not_for_channel_message())
            return

        if not user_manager.check_user(user.id, user.name):
            await ctx.channel.send(responses.not_registed_message())
            return
        
        if not ranking_list:
            await ctx.reply(responses.vote_empty_message())
            return


    @bot.command(name='quit')
    async def quit(ctx):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.5)
            await ctx.channel.send(responses.game_instruction())
            return
        
        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if not user_manager.check_user(user.id, user.name):
            await ctx.reply(responses.not_registed_message())    
            return
        
        if session.channel == ctx.channel:
            user_manager.delete_user(user.id)       # delete user from the list of players
            await ctx.reply(responses.quit_game_message()) 
            embed = discord.Embed(title="List of Players", color=discord.Color.blurple())
            view = gameclasses.StartGame(user_manager, ctx.channel, session)
            if any(user_manager.users.items()):
                for i, (user_id, user_data) in enumerate(user_manager.users.items(), start=1):
                    embed.add_field(name=f"{i}. {user_data['username']}", value="", inline=False)
                await ctx.channel.send(embed=embed, view=view)
            else:
                embed.description = "No players have joined yet."
                await ctx.channel.send(embed=embed)
        else:
            await ctx.reply(responses.not_game_channel_quit_message(session.channel))
        

    # FOR DEBUGGING PURPOSES
    @bot.command(name='print')
    async def print_list(ctx):
        print(user_manager.users)


    # run discord bot token
    bot.run(TOKEN)