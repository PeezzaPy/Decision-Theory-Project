import textwrap

def handle_response(message) -> str:
    process_message = message.lower()

    if process_message in ['hi', 'hello', 'yow', 'zup']:
        response = "Hello, there!" + "\n\n" + help_command()
        return response


    return "I'm new, I don't know what you said"



def help_command():
    return "Use command prefix '!command' to see all my commands."

def game_instruction() -> str:
    return "WALANG INSTRUCTION, MATUTO KA MAGISA!"

def list_command():
    commands = """
        **!command** - see all commands
        **!instr** - display instructions of the game
        **!start** - start the game
        **!stop** - stop the game
        **!join** - register/participate in the game
        **!list** - make a list of food (!list food1, food2, ...)
        **!quit** - quit the game  
    """
    return textwrap.dedent(commands)

def already_joined_message():
    return "You have already joined the game"

def check_direct_message():
    return "I sent you a direct message. Please review and check it out."

def game_channel_message(channel):
    return f"Game has already started to the '**{channel}**' text channel."

def game_players_required_message():
    return " The game requires at least **two** players to begin"

def game_start_message():
    return "The game will start"

def game_stop_message():
    return "The game has been stopped"

def game_terminated_message():
    return "The game stops because there has been no activity for 15 minutes"

def list_create_message():
    message = """
        **Game Started!**\n
        Please provide a list of foods. Use this command:
        **!list** *food1, food2, ...* - create a list of food separate by comma
        \t\t(e.g !list chicken, pork tonkatsu, ...)
    """
    return textwrap.dedent(message)

def list_edit_message():
    message = """
        To proceed, please click the **Submit** button if you are satisfied 
        with the current list. If you wish to modify the list, use ***!list***
        command to overwrite the previous list.
    """
    return textwrap.dedent(message)

def list_empty_message():
    message = """
        List **cannot be empty**. Please provide a list of foods\n
        **!list** *food1, food2, ...* - create a list of food separate by comma
        \t\t(e.g !list chicken, pork tonkatsu, ...)
    """
    return textwrap.dedent(message)

def no_running_game_message():
    return "No game is currently running"

def not_for_channel_message():
    return "NOT HERE!, This command can only be used in a direct message with me"

def not_for_direct_message():
    return "This command can only be used in text channels, not in direct messages"

def not_game_channel_message(channel):
    return f"Cannot stop it here, Please stop it in the '**{channel}**' channel"

def not_game_channel_quit_message(channel):
    return f"Please refrain from leaving the game in other channels. Kindly exit the game in the '**{channel}**' channel instead"

def not_registed_message():
    return "Oops!, it seems you haven't joined the game yet."

def vote_empty_message():
    message = """
        Vote ranking list **cannot be empty**. Please provide a ranking of food preferences\n
        **!vote** *food1, food2, ...* - create a list of food separate by comma
        \t\t(e.g !vote chicken, pork tonkatsu, ...)
    """
    return textwrap.dedent(message)

def vote_instruction():
    message = """
        **!vote** *food1, food2, ...* - make a vote from most preferred (*first*) to least preferred (*last*)
        \t\t(e.g !vote chicken, pork tonkatsu, ... last)
    """ 
    return textwrap.dedent(message)

def quit_game_message():
    return "You have left the game.\nPlease come back and play again soon..."