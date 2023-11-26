from discord.ext import commands
import discord
import time
import asyncio
import responses
import gameclasses
import json

# Read the json file to access the token value
with open('config.json', 'r') as file:
    config_data = json.load(file)

TOKEN = config_data['token']

# global object
session = gameclasses.Session()
user_manager = gameclasses.UserManager()
tasks_loop_runner = gameclasses.TaskLoopBotRunner(user_manager, session)

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
            command_exception_to_whitespace = ['list', 'vote']
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
            await asyncio.sleep(0.2)
            await ctx.channel.send(responses.game_instruction())
            return

        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if ctx.channel != session.channel:
            await ctx.reply(responses.not_game_channel_join_message(session.channel))
            return
        
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

        # Check if the message with the specified embed already exists
        if session.join_message_exist:
            # If it exists, delete the existing message
            await session.join_message_exist.delete()
        session.join_message_exist = await ctx.channel.send(embed=embed, view=view)


    @bot.command(name='start')
    async def start_game(ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if session.game_started:
            await ctx.channel.send(responses.game_channel_message(session.channel))
            return

        tasks_loop_runner.start_game_activity()
        session.set_game_session_status(bot.get_channel(ctx.channel.id))
        # create stylized embed messages
        embed = discord.Embed(
            title="Welcome!",
            description="Voting for preferred foods using IRV algorithm",
            color=discord.Color.dark_teal()
        )      
        embed.add_field(name="", value="", inline=False)          # for space purposes
        embed.add_field(name="Instruction", value=responses.game_instruction())
        embed.set_field_at(0, name="Commands to Use", value=responses.list_command())
        embed.set_image(url="https://media.tenor.com/bfxcDYAwqdAAAAAC/eating-food.gif")
        embed.set_footer(text="Enjoy the game! 🍀")
        
        # if exist remove the previous one
        if session.game_intro:
            await session.game_intro.delete()
            session.game_intro = None           # set default
        session.game_intro = await ctx.channel.send(embed=embed)

    
    @bot.command(name='stop')
    async def stop_game(ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            return
        
        if session.channel == ctx.channel:
            if session.game_intro:          # delete game intro message
                await session.game_intro.delete()
                session.game_intro = None    

            tasks_loop_runner.stop_game_activity()
            tasks_loop_runner.stop_vote_result_button()
            session.set_no_game_session()
            user_manager.default_user()
            await ctx.channel.send(responses.game_stop_message())
        else:
            await ctx.channel.send(responses.not_game_channel_message(session.channel))


    @bot.command(name='list')
    async def get_food_list(ctx, *, food_list=None):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.2)
            await ctx.channel.send(responses.game_instruction())
            return
        
        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command
    
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.send(responses.not_for_direct_message())
            return
        
        if ctx.channel != session.channel:
            await ctx.reply(responses.not_game_channel_create_list_message(session.channel))
            return
        
        # to avoid redundancy of bot messages in LIST
        if session.list_object[0]:
            await session.list_object[0].delete()
            session.list_object[0] = None

        if not user_manager.check_user(user.id, user.name):
            content = responses.not_registed_message() + '\n'
            embed = discord.Embed(color=discord.Color.blurple())
            embed.description = responses.join_quit_players_instruction(session.channel)
            session.list_object[0] = await ctx.channel.send(content=content, embed=embed)
            return
        
        if session.player_accept:
            session.list_object[0] = await ctx.reply(responses.still_accepting_player_message(session.channel) + '\n')
            return
        
        if session.list_submit:
            session.list_object[0] = await ctx.reply(responses.already_submit_list_message())
            return
        
        if session.list_exist:
            session.list_object[0] = await ctx.reply(responses.list_exist_message())
            return
        
        if not food_list:
            session.list_object[0] = await ctx.reply(responses.list_empty_message())
            return

        food_items = [food_item.strip() for food_item in food_list.split(',') if food_item.strip()]
        if food_items:
            session.list_exist = True       # to avoid redundant list
            embed = discord.Embed(title="Food List", color=discord.Color.dark_gold())
            for i, item in enumerate(food_items, start=1):
                embed.add_field(name=f"{i}. {item}", value="", inline=False)
            view = gameclasses.ListMenu(ctx, bot, user_manager, session, food_items)
            content = responses.list_edit_message()
        
            if session.list_object[1]:      # delete orevious object first to avoid redundancy
                await session.list_object[1].delete()
            session.list_object[1] = await ctx.reply(embed=embed, view=view, content=content)
        else:
            content = responses.list_empty_message()
            session.list_object[0] = await ctx.reply(content=content)


    @bot.command(name='vote')
    async def vote_ranking(ctx, *, ranking_list=None):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.2)
            await ctx.channel.send(responses.game_instruction())
            return
        
        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command
        
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.channel.send(responses.not_for_channel_message())
            return
        
        # to remove redundancy of bot messages in VOTE
        if user_manager.get_vote_object(user.id, user.name):
            message = user_manager.get_vote_object(user.id, user.name)
            if message[0]:
                await message[0].delete()
                user_manager.set_vote_error_message_none(user.id, user.name)
                
        if not user_manager.check_user(user.id, user.name):
            content = responses.not_registed_message() + '\n'
            embed = discord.Embed(color=discord.Color.blurple())
            embed.description = responses.join_quit_players_instruction(session.channel)
            user_manager.set_vote_error_message(user.id, user.name, await ctx.channel.send(embed=embed))
            return
        
        if session.player_accept:
            content = responses.still_accepting_player_message(session.channel) + '\n'
            embed = discord.Embed(color=discord.Color.blurple())
            embed.description = responses.join_quit_players_instruction(session.channel)
            user_manager.set_vote_error_message(user.id, user.name, await ctx.reply(content=content, embed=embed))
            return

        if not session.list_exist:
            user_manager.set_vote_error_message(user.id, user.name, await ctx.channel.send(responses.list_not_exist_message(session.channel)))
            return

        if user_manager.is_player_food_ranking_list(user.id, user.name):
            user_manager.set_vote_error_message(user.id, user.name, await ctx.channel.send(responses.already_submit_vote_message()))
            return
        
        if user_manager.is_ranking_list_exist(user.id, user.name):
            user_manager.set_vote_error_message(user.id, user.name, await ctx.reply(responses.vote_only_once_message()))
            return

        if not ranking_list:
            user_manager.set_vote_error_message(user.id, user.name, await ctx.reply(responses.vote_empty_message() + '\n' + responses.vote_instruction()))
            return
        
        ranked_food_items = [rank_item.strip() for rank_item in ranking_list.split(',') if rank_item.strip()]
        not_in_food_list = []
        if ranked_food_items:
            for item in ranked_food_items:
                if item.lower() not in session.food_list:
                    not_in_food_list.append(item)
        
            if not not_in_food_list:
                user_manager.set_vote_exist(user.id, user.name)         # add bool, if initial list exist
                embed = discord.Embed(title="Preference Ranking of Foods", color=discord.Color.dark_gold())
                for i, item in enumerate(ranked_food_items, start=1):
                    embed.add_field(name=f"{i}. {item}", value="", inline=False)
                view = gameclasses.VoteMenu(ctx, user_manager, session, ranked_food_items)
                content = responses.vote_edit_message()
                await ctx.reply(embed=embed, view=view, content=content)
            else:
                embed = view = None
                content = responses.vote_not_in_food_list_message(not_in_food_list)
                user_manager.set_vote_error_message(user.id, user.name, await ctx.reply(embed=embed, view=view, content=content))
        else:
            embed = view = None
            content = responses.vote_empty_message() + '\n' + responses.vote_instruction()
            user_manager.set_vote_error_message(user.id, user.name, await ctx.reply(embed=embed, view=view, content=content))


    @bot.command(name='quit')
    async def quit(ctx):
        if not session.get_game_session_status():
            await ctx.channel.send(responses.no_running_game_message())
            await asyncio.sleep(0.2)
            await ctx.channel.send(responses.game_instruction())
            return
        
        session.last_activity_time = time.time()            # record last activity time
        user = ctx.author                                   # Get the user who invoked the command

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.reply(responses.not_for_direct_message())
            return
        
        if not user_manager.check_user(user.id, user.name):
            await ctx.reply(responses.not_registed_message() + '\n')
            await asyncio.sleep(0.2)
            embed = discord.Embed(color=discord.Color.blurple())
            embed.description = responses.join_quit_players_instruction(session.channel)
            await ctx.channel.send(embed=embed)
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
        ...


    # run discord bot token
    bot.run(TOKEN)
