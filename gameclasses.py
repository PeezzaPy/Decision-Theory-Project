from irv import determine_irv_winner
from dataclasses import dataclass
import responses
import discord
import time

process_string = None

@dataclass
class Session:
    game_started = False
    game_intro = [None, None]      # exempted to default
    game_quit = [None, None]
    channel = None
    last_activity_time = None
    player_accept = True
    food_list = None
    list_exist = False
    list_submit = False
    join_message_object = [None, None]
    list_object = [None, None]
    submit_button_message = None
    total_submit_player = 0
    result_button_message = [None, None]
    task_loop_runner = None
    is_result = False

    def set_game_session_status(self, channel: str):      
        self.game_started = True
        self.channel = channel
        self.last_activity_time = time.time()   

    async def set_no_game_session(self):
        if self.game_intro[0]:
            await self.game_intro[0].delete()
        if self.game_intro[1]:
            await self.game_intro[1].delete()
        self.game_intro = [None, None]

        if self.game_quit[0]:
            await self.game_quit[0].delete()
        if self.game_quit[1]:      
            await self.game_quit[1].delete()
        self.game_quit = [None, None]

        if self.join_message_object[1]:      
            await self.join_message_object[1].delete()
        self.join_message_object = [None, None]

        if self.list_object[0]:
            await self.list_object[0].delete()
        if self.list_object[1]:      
            await self.list_object[1].delete()
        self.list_object = [None, None]

        if self.result_button_message[1]:      
            await self.result_button_message[1].delete()
        self.result_button_message = [None, None]

        self.game_started = False
        self.channel = None
        self.last_activity_time = None
        self.player_accept = True
        self.food_list = None
        self.list_exist = False
        self.list_submit = False
        self.total_submit_player = 0
        self.task_loop_runner = None
        self.is_result = False

    def get_game_session_status(self):
        if self.game_started and self.channel and self.last_activity_time:
            return True
        return False
    
    def __repr__(self):
        return f"Channel: {self.channel} | Last Activity Time: {self.last_activity_time}"


class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user_id: int, username: str):
        if user_id not in self.users:
            self.users[user_id] = {'username': username}
            return True
        return False
    
    def add_food_ranking_list(self, user_id: int, username: str, food_ranking_list: str):
        if not any(self.users.items()):
            return False
        
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                self.users[id]['food ranking list'] = food_ranking_list
                return True
        return False
    
    def check_user(self, user_id: int, username: str):
        if len(self.users) == 0:
            return False
        return user_id in self.users and self.users[user_id]['username'] == username

    def delete_vote_exist(self, user_id: int, username: str):  
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                self.users[id].pop('vote ranking exist')

    def default_user(self):
        self.users.clear()

    def delete_user(self, user_id: int):
        if len(self.users) == 0:
            return False
        
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
 
    def get_submit(self, user_id: int, username: str):
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                return value.get('submitted')

    def get_vote_object(self, user_id: int, username: str):  
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                return value.get('vote object')

    def is_ranking_list_exist(self, user_id: int, username: str):
        if not any(self.users.items()):
            return False
        
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username and value.get('vote ranking exist') is not None:
                return True
        return False
    
    def is_player_food_ranking_list(self, user_id: int, username: str):
        if not any(self.users.items()):
            return False
        
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username and value.get('food ranking list') is not None:
                return True
        return False

    def set_submit(self, user_id: int, username: str):
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                    self.users[id]['submitted'] = True

    def set_vote_embed(self, user_id: int, username: str, vote_message):
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                if 'vote object' in self.users[id]:         # if exist
                    self.users[id]['vote object'][1] = vote_message
                else:
                    self.users[id]['vote object'] = [None, vote_message]
                break

    def set_vote_error_message(self, user_id: int, username: str, vote_error_message):  
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                if 'vote object' in self.users[id]:         # if exist
                    self.users[id]['vote object'][0] = vote_error_message  
                else:
                    self.users[id]['vote object'] = [vote_error_message]
                break
    
    def set_vote_error_message_none(self, user_id: int, username: str):  
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                self.users[id]['vote object'][0] = None
            
    def set_vote_exist(self, user_id: int, username: str):        
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                self.users[id]['vote ranking exist'] = True
                break


class ListMenu(discord.ui.View):
    def __init__(self, ctx, bot, user_manager: UserManager, session: Session, food_list: str):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.user_manager = user_manager
        self.session = session
        self.food_list = food_list

    async def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):   
        if self.session.game_started:
            self.session.list_submit = True
        # Iterate through participants and send a direct message to each of them
        await self.disable_all_buttons()
        new_embed = discord.Embed(title="Submitted", color=discord.Color.green())
        await interaction.response.edit_message(content=None, embed=new_embed, view=self)
        self.session.food_list = self.food_list          # pass the value of food list to session class
        # message to make sure it is submitted on channel 
        await interaction.channel.send(responses.check_direct_message())            

        for user_id, value in self.user_manager.users.items():
            user = await self.bot.fetch_user(user_id)
            # Send a direct message to each user
            if user:
                try:
                    await user.send(f"Hello **{value['username']}**! Here are the list of food choices:")
                    embed = discord.Embed(title="Voting List", color=discord.Color.dark_orange())
                    for i, food in enumerate(self.food_list, start=1):
                        embed.add_field(name=f"**{i}.** {food}", value="", inline=False)

                    self.user_manager.set_vote_embed(self.ctx.author.id, self.ctx.author.name, await user.send(embed=embed))
                    await user.send(responses.vote_instruction())                   
                except discord.HTTPException:
                    print(f"Failed to send a message to {value['username']} | id: {user_id}")
                    await interaction.response.send_message("Error occurred while submitting") 

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.session.game_started:
            self.session.list_exist = False
        await self.disable_all_buttons()
        new_embed = discord.Embed(title="List deleted", color=discord.Color.red())
        await interaction.response.edit_message(content=None, embed=new_embed, view=self)         # delete the message
        if self.session.list_object[0]:             # delete validation messages too if exist
            await self.session.list_object[0].delete()
            self.session.list_object[0] = None
        self.session.list_object[0] = await interaction.followup.send(responses.list_create_message())


class VoteMenu(discord.ui.View):
    def __init__(self, ctx, user_manager: UserManager, session: Session, food_ranking_list: str, tasks_loop_runner):
        super().__init__()
        self.ctx = ctx
        self.user_manager = user_manager
        self.session = session
        self.food_ranking_list = food_ranking_list
        self.tasks_loop_runner = tasks_loop_runner
    
    async def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.disable_all_buttons()
        self.session.total_submit_player += 1
        self.user_manager.add_food_ranking_list(self.ctx.author.id, self.ctx.author.name, self.food_ranking_list)
        self.user_manager.set_submit(self.ctx.author.id, self.ctx.author.name)
        new_embed = discord.Embed(title="Submitted", color=discord.Color.green())
        await interaction.response.edit_message(content=None, embed=new_embed, view=self)
        
        #inform everyone in game channel, if player submitted
        await self.session.channel.send(f"Player **{self.ctx.author.name}** has **submitted!**")

        if self.session.total_submit_player == 1:           # display the evaluate button
            if not self.tasks_loop_runner.vote_result_button.is_running():
                self.tasks_loop_runner.vote_result_button.start()

        if self.session.total_submit_player > 1:        # tasks loop first before this
            if self.session.result_button_message[1]: 
                await self.session.result_button_message[1].delete()
                self.session.result_button_message[1] = None
            self.session.result_button_message[1] = await self.session.channel.send(view=self.session.result_button_message[0])
        
        # if self.session.total_submit_player > 1:
        #     self.session.result_button_message[0].enable_button()
 
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.disable_all_buttons()
        self.user_manager.delete_vote_exist(self.ctx.author.id, self.ctx.author.name)       # delete existing initial list
        new_embed = discord.Embed(title="Vote List deleted", color=discord.Color.red())
        await interaction.response.edit_message(content=None, embed=new_embed, view=self)
        # bump the voting list
        if self.user_manager.get_vote_object(self.ctx.author.id, self.ctx.author.name):
            bump_message = previous_message = self.user_manager.get_vote_object(self.ctx.author.id, self.ctx.author.name)
            if previous_message[1]:
                await previous_message[1].delete()
                self.user_manager.set_vote_embed(
                    self.ctx.author.id,
                    self.ctx.author.name,
                    await interaction.followup.send(content=responses.vote_create_message() + '\n' + 
                                                    responses.vote_instruction(), 
                                                    embed=bump_message[1].embeds[0])
                )


class CheckResult(discord.ui.View):
    def __init__(self, user_manager: UserManager, session: Session, tasks_loop_runner):
        super().__init__()
        self.user_manager = user_manager
        self.session = session
        self.tasks_loop_runner = tasks_loop_runner
       
    def end_session(self):
        global process_string
        # END SESSION
        process_string = None      # set to default
        if self.tasks_loop_runner.update_game_activity.is_running():
            self.tasks_loop_runner.update_game_activity.stop()
        if self.tasks_loop_runner.vote_result_button.is_running():
            self.tasks_loop_runner.vote_result_button.stop()
        self.session.set_no_game_session()
        self.user_manager.default_user()

    async def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(label="Get Result", style=discord.ButtonStyle.primary)
    async def get_result(self, interaction: discord.Interaction, button: discord.ui.Button):
        global process_string

        embed = discord.Embed(color=discord.Color.dark_teal())
        if not self.session.get_game_session_status():
            await self.disable_all_buttons()
            embed.add_field(name="❓ NO GAME FOUND ❓", value="Use command **!start** to initialize a game")
            await interaction.response.edit_message(embed=embed, view=self)
        elif self.session.total_submit_player < len(self.user_manager.users):
            embed.add_field(name="❌ UNABLE TO EVALUATE ❌", value="All players need to submit their votes")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await self.disable_all_buttons()
            copy_users = self.user_manager.users            # get a copy
            # enter IRV algorithm to process votes
            winner = determine_irv_winner(copy_users, self.session.food_list)
            # winner, process_string = determine_irv_winner(copy_users, self.session.food_list)
            embed.add_field(name="✅ EVALUATION SUCCESSFUL! ✅", value=f"**\nWinner: {winner}**", inline=False)
            # embed.add_field(name="PROCESS USING IRV ALGORITHM", value="", inline=False)
            # embed.add_field(name="", value=process_string, inline=True)
            await interaction.response.edit_message(embed=embed, view=self)


class SeeProcessResult(discord.ui.View):
    def __init__(self):
        super().__init__()


class StartGame(discord.ui.View):
    def __init__(self, user_manager: UserManager, channel: discord.TextChannel, session: Session):
        super().__init__()
        self.user_manager = user_manager
        self.channel = channel
        self.session = session

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.user_manager.users) < 2:            # need 2 or more players to start
            embed = discord.Embed(color=discord.Color.brand_red())
            embed.add_field(name=responses.game_players_required_message(), value="")
            await interaction.response.send_message(embed=embed)
            # If the list message exist, delete the existing message
            if self.session.join_message_object[1]:
                temp_message_object = self.session.join_message_object[1]
                await temp_message_object.delete()
                self.session.join_message_object[1] = None
            # bump the list of joining players
            self.session.join_message_object[1] = await interaction.followup.send(embed=self.session.join_message_object[0], view=self)
            return
       
        button.disabled = True
        self.session.player_accept = False
        embed = discord.Embed(color=discord.Color.dark_teal())
        embed.add_field(name=responses.game_started_message(), value=responses.list_create_message())
        await interaction.response.edit_message(embed=embed, view=self)
            

