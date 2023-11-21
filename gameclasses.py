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

    def set_game_session_status(self, channel: str):      
        self.game_started = True
        self.channel = channel
        self.last_activity_time = time.time()   

    def set_no_game_session(self):
        self.game_started = False
        self.channel = None
        self.last_activity_time = None
        self.player_accept = True

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
    
    def add_food_list(self, user_id: int, username: str, food_list: str):
        if not any(self.users.items()):
            return False
        
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username:
                self.users[id]['food list'] = food_list
                return True
        return False
    
    def default_user(self):
        self.users.clear()

    def check_food_list(self, user_id: int, username: str):
        if not any(self.users.items()):
            return False
        
        for id, value in self.users.items():
            if id == user_id and value.get('username') == username and value.get('food list') is not None:
                return True
        return False
    
    def check_user(self, user_id: int, username: str):
        if len(self.users) == 0:
            return False
        return user_id in self.users and self.users[user_id]['username'] == username

    def delete_user(self, user_id: int):
        if len(self.users) == 0:
            return False
        
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False



class ListMenu(discord.ui.View):
    def __init__(self, user_manager: UserManager, bot, food_list: str):
        super().__init__()
        self.user_manager = user_manager
        self.bot = bot
        self.food_list = food_list

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Iterate through participants and send a direct message to each of them
        button.disabled = True
        await interaction.response.edit_message(view=self)
        for user_id, value in self.user_manager.users.items():
            user = await self.bot.fetch_user(user_id)
            # Send a direct message to each user
            if user:
                try:
                    await user.send(f"Hello **{value['username']}**! Here are the list of food choices:")
                    embed = discord.Embed(title="Voting List", color=discord.Color.dark_orange())
                    for i, food in enumerate(self.food_list, start=1):
                        embed.add_field(name=f"**{i}.** {food}", value="", inline=False)

                    # message to make sure it is submitted on channel
                    await interaction.channel.send("**Submitted!**\n" + (responses.check_direct_message()))
                    await user.send(embed=embed)
                    await user.send(responses.vote_instruction())
                except discord.HTTPException:
                    print(f"Failed to send a message to {value['username']} | id: {user_id}")
                    await interaction.response.send_message("Error occurred while submitting")


class StartGame(discord.ui.View):
    def __init__(self, user_manager: UserManager, channel: discord.TextChannel, session: Session):
        super().__init__()
        self.user_manager = user_manager
        self.channel = channel
        self.session = session

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
       if len(self.user_manager.users) < 2:
           await interaction.response.send_message(responses.game_players_required_message())
           return
       
       button.disabled = True
       self.session.player_accept = False
       await interaction.response.edit_message(view=self)
       await self.channel.send(responses.list_create_message())