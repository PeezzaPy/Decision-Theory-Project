import random


def vote_count_per_choice(users, vote_count):
    for user_info in users.values():
        if user_info.get('food ranking list'):          # if not empty list
            for choice in user_info['food ranking list']:
                vote_count[choice] += 1
                break                    # only the first choice
    return vote_count


def determine_irv_winner(users, food_list):
    global process_string     
    iter = 0       

    # Create a set of all unique choices  
    random.seed()                                        # random seed
    vote_count = {vote: 0 for vote in food_list}         # dict comprehension
    vote_count = vote_count_per_choice(users, vote_count)
    total_votes = sum(vote_count.values())               # get the total votes of first choice
    
    # TROUBLESHOOT PURPOSES
    print(f"Preprocessed Data: (Total votes: {total_votes})")
    debugging(users)

    while True:
        # Initialize the votes for each food choice
        vote_count = {vote: 0 for vote in food_list}       # dict comprehension
        vote_count = vote_count_per_choice(users, vote_count)
        print(f"Vote count: {vote_count}")

        # Find the candidates with the lowest votes except zero (0)
        non_zero_votes = {vote: count for vote, count in vote_count.items() if count != 0}
        
        # Get the candidate(s) with minimum vote
        min_votes = min(vote_count.values())
        min_candidates = [choice for choice, votes in vote_count.items() if votes == min_votes]
        selected_min_candidate = random.choice(min_candidates)
        print(f"Selected min candidate: {selected_min_candidate}")
        
        # Get the candidate(s) with maximum vote
        max_votes = max(vote_count.values())
        max_candidates = [choice for choice, votes in vote_count.items() if votes == max_votes]
        selected_max_candidate = random.choice(max_candidates)
        print(f"Selected max candidate: {selected_max_candidate}")

        # # Get the candidate(s) with minimum vote
        # min_votes = min(non_zero_votes.values())
        # min_candidates = [choice for choice, votes in vote_count.items() if votes == min_votes]
        # selected_min_candidate = random.choice(min_candidates)
        # print(f"Selected min candidate: {selected_min_candidate}")
        
        # # Get the candidate(s) with maximum vote
        # max_votes = max(non_zero_votes.values())
        # max_candidates = [choice for choice, votes in vote_count.items() if votes == max_votes]
        # selected_max_candidate = random.choice(max_candidates)
        # print(f"Selected max candidate: {selected_max_candidate}")

        # # if only one element has vote
        # if len(non_zero_votes) == 1:
        #     result_key = list(non_zero_votes.keys())[0]
        #     winner = result_key.replace("(", "").replace(")", "") 
        #     print(f"\nWinner:  {winner}")
        #     return winner
        
                # No majority
        if len(min_candidates) == len(food_list):
            print(f"\nNo clear winner. Tied candidates: {min_candidates}")
            return min_candidates
        
        # Return already the winner if the min_votes is greater than quota (total_votes/2 + 1)
        if max_votes >= (total_votes // 2 + 1):
            print(f"\nWinner:  {selected_max_candidate}")
            return selected_max_candidate 

        # Eliminate the candidate(s) vote with the least vote
        for user_info in users.values():
            user_info['food ranking list'] = [
                choice for choice in user_info['food ranking list'] 
                if choice not in selected_min_candidate
            ]

        if selected_min_candidate in food_list:
            food_list.remove(selected_min_candidate)
        
        #TROUBLESHOOT PURPOSES
        iter += 1
        print(f"\n==================================================================\n\n\t\t({iter}) Iteration: \n")
        debugging(users)


#TROUBLESHOOT PURPOSES
def debugging(users):
    for user_info in users.values():
        print(f"User: {user_info['username']}  |  Food List: {user_info['food ranking list']}") 
    


# FOR EXPERIMENTAL PURPOSES
# list_choices = ["A", "B", "C", "D", "E"]

# users = {
#     'user1': {
#         'username': "Johnson",
#         'food ranking list': ["A", "B", "C"]
#     },
#     'user2': {
#         'username': "Patrick",
#         'food ranking list': ["B", "A", "D", "C"]
#     },
#     'user3': {
#         'username': "Martin",
#         'food ranking list': ["D", "A", "C"]
#     },
#     'user4': {
#         'username': "Marikina",
#         'food ranking list': ["A", "B"]
#     },
#     'user5': {
#         'username': "Garfield",
#         'food ranking list': ["B", "A", "C"]
#     },
#     'user6': {
#         'username': "Gorilla",
#         'food ranking list': ["B", "D", "C", "A"]
#     },
#     'user7': {
#         'username': "Pepito",
#         'food ranking list': ["E", "C", "D", "A"]
#     }
# }
    

# if __name__ == "__main__":
#     determine_irv_winner(users, list_choices)
#     print(process_string)