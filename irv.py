import time

def vote_count_per_choice(users, vote_count):
    for user_info in users.values():
        for choice in user_info['food ranking list']:
            vote_count[choice] += 1
            break           # only the first choice
    return vote_count


def determine_irv_winner(users, food_list):
    # Create a set of all unique choices  
    vote_count = {vote: 0 for vote in food_list}         # dict comprehension

    vote_count = vote_count_per_choice(users, vote_count)
    total_votes = sum(vote_count.values())          # get the total votes of first choice
    
    # TROUBLESHOOT PURPOSES
    # print(f"Total votes: {total_votes}")
    # debugging(users)

    while True:
        # Initialize the votes for each food choice
        vote_count = {vote: 0 for vote in food_list}       # dict comprehension
        vote_count = vote_count_per_choice(users, vote_count)
        print(f"Vote count: {vote_count}")  

        # Find the candidates with the lowest votes except zero (0)
        non_zero_votes = {vote: count for vote, count in vote_count.items() if count != 0}
        
        # Get the candidate(s) with minimum vote
        min_votes = min(non_zero_votes.values())
        print(f"Min votes: {min_votes}")
        min_candidates = [choice for choice, votes in vote_count.items() if votes == min_votes]

        # Get the candidate(s) with maximum vote
        max_votes = max(non_zero_votes.values())
        print(f"Max votes: {max_votes}")
        max_candidates = [choice for choice, votes in vote_count.items() if votes == max_votes]

        # Return already the winner if the min_votes is greater than quota (total_votes/2 + 1)
        if max_votes >= (total_votes // 2 + 1):
            return max_candidates

        # Eliminate the candidate(s) vote with the least vote
        for user_info in users.values():
            user_info['food ranking list'] = [choice for choice in user_info['food ranking list'] if choice not in min_candidates]
        
        # TROUBLESHOOT PURPOSES
        # print(f"Total votes: {total_votes}")
        # debugging(users)

# TROUBLESHOOT PURPOSES
# def debugging(users):
#     for user_info in users.values():
#         print(user_info['name'], end=" ")
#         print(user_info['food ranking list'])
#     time.sleep(3)

# list_choices = ["A", "B", "C", "D", "E"]

# users = {
#     'user1': {
#         'name': "Johnson",
#         'food ranking list': ["A", "B", "C"]
#     },
#     'user2': {
#         'name': "Patrick",
#         'food ranking list': ["B", "A", "D", "C"]
#     },
#     'user3': {
#         'name': "Martin",
#         'food ranking list': ["D", "A", "C"]
#     },
#     'user4': {
#         'name': "Marikina",
#         'food ranking list': ["A", "B"]
#     },
#     'user5': {
#         'name': "Garfield",
#         'food ranking list': ["B", "A", "C"]
#     },
#     'user6': {
#         'name': "Gorilla",
#         'food ranking list': ["B", "D", "C", "A"]
#     },
#     'user7': {
#         'name': "Pepito",
#         'food ranking list': ["E", "C", "D", "A"]
#     }
# }
    