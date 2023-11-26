from dataclasses import dataclass
import responses
import discord
import time

@dataclass
class Session:
    game_started = False
    channel = None
    last_activity_time = None
    player_accept = True
    food_list = None
    list_exist = False
    list_submit = False
    join_message_exist = None
    list_object = [None, None]

    def set_game_session_status(self, channel: str):      
        self.game_started = True
        self.channel = channel
        self.last_activity_time = time.time()   

    def set_no_game_session(self):
        self.game_started = False
        self.channel = None
        self.last_activity_time = None
        self.player_accept = True
        self.food_list = None
        self.list_exist = False
        self.list_submit = False
        self.join_message_exist = None
        self.list_object = [None, None]

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
        await interaction.channel.send(responses.check_direct_message())            # message to make sure it is submitted on channel 

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
    def __init__(self, ctx, user_manager: UserManager, session: Session, food_ranking_list: str):
        super().__init__()
        self.ctx = ctx
        self.user_manager = user_manager
        self.session = session
        self.food_ranking_list = food_ranking_list
    
    async def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.disable_all_buttons()
        self.user_manager.add_food_ranking_list(self.ctx.author.id, self.ctx.author.name, self.food_ranking_list)
        new_embed = discord.Embed(title="Submitted", color=discord.Color.green())
        await interaction.response.edit_message(content=None, embed=new_embed, view=self)
        #inform everyone in game channel, if player submitted
        await self.session.channel.send(f"Player **{self.ctx.author.name}** has **submitted!**")
        
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


class StartGame(discord.ui.View):
    def __init__(self, user_manager: UserManager, channel: discord.TextChannel, session: Session):
        super().__init__()
        self.user_manager = user_manager
        self.channel = channel
        self.session = session

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
       if len(self.user_manager.users) < 1:
           await interaction.response.send_message(responses.game_players_required_message())
           return
       
       button.disabled = True
       self.session.player_accept = False
       await interaction.response.edit_message(view=self)
       await self.channel.send(responses.game_started_message() + '\n' + responses.list_create_message())