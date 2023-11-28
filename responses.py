from discord import TextChannel, DMChannel
import textwrap

def handle_response(ctx, message):
    process_message = message.lower()

    if process_message in ['hi', 'hello', 'yow', 'zup']:
        if isinstance(ctx.channel, TextChannel):
            return f"**Hello {ctx.author.mention}!**\n\n\u2193 Below here are my commands \u2193"
        elif isinstance(ctx.channel, DMChannel):
            return f"**Hello there, my friend!**\n\n\u2193 Below here are my commands \u2193"
    # if just mentioned, no other text
    elif process_message == "":
        return f"**Hello there**, I heard my name!\n\n\u2193 Here's how you can make the most of my capabilities \u2193"
      
    return "Sorry, I don't know what you said"

def already_joined_message():
    return "You have already joined the game"

def already_submit_list_message():
    return "The list has already been **submitted**, and changes are no longer possible." 

def already_submit_vote_message():
    return "You have already **submitted** your preferred ranking of choice/s"

def check_direct_message():
    return "I sent a **direct message to every player**. Please review and check it out."

def game_channel_message(channel):
    return f"Game has already started to the '**{channel}**' text channel."

def game_instruction() -> str:
    message = f"""
        ➡️ Type **!start** command in any __text channel__, to initialize a game\n
        ➡️ Players who wants to join the game will use **!join** command in the __game channel__, then click '**Start**' button\n
        ➡️ Then the game begins, any player should decide and create a list of choices in the game channel using the **!list** command in the __game channel__, from which people will later vote\n
        ➡️ The bot will direct message each and every player to vote from a given list using **!vote** command in __direct messages__ with bot, then '**Submit**'\n
        ➡️ Wait for everyone and once you're all done, go back to game channel and click '**Get Result**' button\n
    """
    return textwrap.dedent(message)

def init_game_instruction() -> str:
    message = f"""
        ➡️ Type **!join** command in the __game channel__ for those who wants to join, then click '**Start**' button\n
        ➡️ Then the game begins, any player should decide and create a list of choices using the **!list** command in the __game channel__, from which people will later vote\n
        ➡️ The bot will direct message each and every player to vote from a given list using **!vote** command in __direct messages__ with bot, then '**Submit**'\n
        ➡️ Wait for everyone and once you're all done, go back to game channel and click '**Get Result**' button\n
    """
    return textwrap.dedent(message)
def game_players_required_message():
    return " The game requires at least **two** players to begin"

def game_started_message():
    return "**Game Started!** 🎲"

def game_stop_message():
    return "The game has been stopped"

def game_terminated_message():
    return "The game stops because there has been no activity for 15 minutes"

def join_quit_players_instruction(channel):
    message = f"""
        To join the game, use the command '**!join**' in the '**{channel}**' channel, where the game 
        is initiated, to participate. And use command '**!quit**' if you wish to withdraw before the 
        game starts. To start the game, click the '**Start**' button instead.
    """
    return textwrap.dedent(message)

def list_command():
    commands = """
        *!command* - see all commands
        *!instr* - display game instructions
        *!start* - start the game
        *!stop* - stop the game
        *!join* - register/participate
        *!list* - make a list of food
        *!vote* - make a ranking of choice
        *!quit* - quit the game  
    """
    return textwrap.dedent(commands)

def list_create_message():
    message = """
        Please provide a list of foods. Use this command:
        **!list** *food1, food2, ...* - create a list of food separate by comma
        \t\t(e.g !list chicken, pork tonkatsu, ...)
    """
    return textwrap.dedent(message)

def list_edit_message():
    message = """
        To proceed, please click the '**Submit**' button if you are satisfied with the current list. 
        If you wish to modify the list, click "**Delete**" button first, then use ***!list*** command to create new list.
    """
    return textwrap.dedent(message)

def list_empty_message():
    message = """
        List **cannot be empty**. Please provide a list of foods\n
        **!list** *food1, food2, ...* - create a list of food separate by comma
        \t\t(e.g !list chicken, pork tonkatsu, ...)
    """
    return textwrap.dedent(message)

def list_not_exist_message(channel):
    message = f"""
        Food list does not exist. Before activating the **!vote** command, please create a list first in the '**{channel}**' channel.\n
        To provide a list of foods. Use this command:
        **!list** *food1, food2, ...* - create a list of food separate by comma
        \t\t(e.g !list chicken, pork tonkatsu, ...)
    """
    return textwrap.dedent(message)

def list_exist_message():
    return "The list still exists. Please click the '**Delete**' button before creating new ones."

def no_running_game_message():
    return "No game is currently running"

def not_for_channel_message():
    return "NOT HERE!, This command can only be used in a direct message with me"

def not_for_direct_message():
    return "This command can only be used in text channels, not in direct messages"

def not_game_channel_message(channel):
    return f"Cannot stop it here, Please stop it in the '**{channel}**' channel"

def not_game_channel_create_list_message(channel):
    return f"Please refrain from creating list in other channels. Kindly create list in the '**{channel}**' channel instead"

def not_game_channel_join_message(channel):
    return f"Please refrain from joining the game in other channels. Kindly join the game in the '**{channel}**' channel instead"

def not_game_channel_quit_message(channel):
    return f"Please refrain from leaving the game in other channels. Kindly exit the game in the '**{channel}**' channel instead"

def not_registed_message():
    return "Oops!, it seems you haven't joined the game yet."

def still_accepting_player_message(channel):
    message = f"""
        The game has not officially started yet in '**{channel}**' channel,
        I am still accepting players who want to join.
    """
    return textwrap.dedent(message)

def vote_create_message():
    return "Please provide a ranking of food preferences"

def vote_edit_message():
    message = """
        To submit, please click the '**Submit**' button if you are satisfied with the current ranking of food preferences. 
        If you wish to modify the list, click '**Delete**' button first, then use ***!vote*** command to create new ranking list.
    """
    return textwrap.dedent(message)

def vote_empty_message():
    return "Vote ranking list **cannot be empty**. Please provide a ranking of food preferences"

def vote_instruction():
    message = """
        **!vote** *food1, food2, ...* - make a vote from most preferred (*first*) to least preferred (*last*)
        \t\t(e.g !vote chicken, pork tonkatsu, ... last)
    """ 
    return textwrap.dedent(message)

def vote_not_in_food_list_message(not_in_food_list):
    if len(not_in_food_list) == 1:
        return f"Food item '**{not_in_food_list[0]}**' not in the list"
    elif len(not_in_food_list) > 1:
        not_in_food_list_str = ', '.join(f"'**{item}**'" for item in not_in_food_list)
        return f"Food items {not_in_food_list_str} not in the list"
    else:
        return "All items are in the list"

def vote_only_once_message():
    return "You can only vote **once**! Delete first your previous preference ranking of food before voting a new one"

def quit_game_message():
    return "You have left the game.\nPlease come back and play again soon..."