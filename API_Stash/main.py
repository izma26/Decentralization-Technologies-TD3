import requests
import random
import numpy as np 
import json 

### Notes
### - The URL of the nodes can be changed inside the database.json file
###   - If they are set to "random", this will generate an random prediction for testing purposes
###   - If it is set to a path (localhost or ngrok) and have an error, use the http protocol instead
### - You can verify any prediction of your choice by toggling the AUTOMATED_INPUT flag to False
###   You will be prompted to test your own values for the consensus prediction  
### - If you have trouble loading the JSON database, you can replace the whole content by :
"""
{
    "nodes": [
        {
            "id": 0,
            "user": "Mathys",
            "URL": "http://localhost:5000/",
            "trust": 0,
            "responses": 24,
            "stake": 46.0
        },
        {
            "id": 1,
            "user": "Ismael",
            "URL": "random",
            "trust": 0,
            "responses": 30,
            "stake": 1994.0
        },
        {
            "id": 2,
            "user": "Hilal",
            "URL": "random",
            "trust": 0.016666666666666666,
            "responses": 30,
            "stake": 978.0
        },
        {
            "id": 3,
            "user": "Adryann",
            "URL": "random",
            "trust": 0.11666666666666667,
            "responses": 30,
            "stake": 3982.0
        }
    ],
    "balance": [
	[
            [
                0,
                1000
            ],
            [
                1,
                2000
            ],
            [
                2,
                1000
            ],
            [
                3,
                4000
            ]
        ]
    ]
}
""" 

AUTOMATED_INPUT = True

# Nodes
nodes = [] 

# Load nodes from the JSON database
with open('./API_Stash/database.json', 'r') as db :

    nodes = json.loads("".join(db.readlines()))["nodes"]

print(f"Nodes loaded : {len(nodes)}")

# Balance history 

balance = [] 

# Load nodes from the JSON database
with open('./API_Stash/database.json', 'r') as db :

    balance = json.loads("".join(db.readlines()))["balance"]

print("Latest balance loaded : ", balance[0])

# We apply the last balance value to the loaded nodes 
for i in balance[0] :
    nodes[i[0]]["stake"] = i[1]
    print(f"Balance updated for user {nodes[i[0]]["user"]} : {nodes[i[0]]["stake"]}")

headers = {
    "content-type" : "application/x-www-form-urlencoded"
}

flowers = ['setosa', 'versicolor', 'virginica']

def input_float(message : str) -> float :

    f : float = -1

    while f < 0 :

        try : 

            f = float(input(message))

        except : 
            print("Invalid input type, provide a floating point number !")

    return f


def get_user_input(automated : bool = True) :

    if automated :

        return [random.uniform(0.0, 2.0) for _ in range(4)]

    response = []

    response.append(input_float("Sepal length : "))
    response.append(input_float("Sepal width : "))
    response.append(input_float("Petal length : "))
    response.append(input_float("Petal width : "))

    return response


def get_nodes(user_input : list):

        # User input should provide 4 values
        if len(user_input) != 4 : 
            print("Invalid user input length !")
            return

        # All 4 values must be floats
        if not(np.all([ type(i) == float  for i in user_input])) :
            print("Invalid input type")
            return

        # We will redistribute the stakes of each node depending on their response
        # The global stake (pool) will be redistributed to 'winning' nodes
        pool = 0

        # Group node id response per flower
        response = { f:[] for f in flowers }

        # Get all predictions from the ngrok nodes
        for node in nodes :

            # If no url is provided, generate a random node response
            if node['URL'] == 'random' :

                response[flowers[int(random.uniform(0, 3))]].append(node["id"])

            else : 

                data = {
                    "sepal_length":user_input[0], 
                    "sepal_width":user_input[1], 
                    "petal_length":user_input[2], 
                    "petal_width":user_input[3]
                }

                # Retrieve answer from listed API
                try :

                    api_response = requests.post(node["URL"]+'predict', headers=headers, data=data).json()

                    # Valid JSON response from the node
                    if "response" in api_response :

                        response[api_response["response"]].append(node["id"])
                        print("Response received from node : ", node["id"], " with value : ", api_response["response"])

                    # Invalid response, node penalized
                    else :

                        print("No valid answer from node : ", node["id"])
                        pool += node['stake']/2
                        node['stake']/=2

                # No response or error, node penalized
                except : 
                    print("No answer from node : ", node["id"])
                    pool += node['stake']
                    node['stake'] = 0

        return response, pool
 

def apply_slash(response : tuple) :
    """Sort results, defines winner and losers and apply trust ratio modification according to results.
    Also applies slash to node stakes

    Args:
        response (tuple): The result of the node data gathering and pool : [node response, pool]
    """
    result = response[0]
    pool = response[1]

    print("Pool value : ", pool)

    # Node result should contain all flowers as keys
    if not(np.all([k in result for k in flowers])) :
        print("Invalid node responses !")
        return

    # Get the number of votes

    nb_answers = np.sum([len(result[k]) for k in result ])
    print("Number of voters : ", nb_answers)

    # We get the most voted flower
    
    # We sort the dictionary by array length (https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value)
    sort = sorted(result.items(), key=lambda item : len(item[1]), reverse=True)
    print(sort)

    # Check equality between top 2 answers
    if len(sort[0][1]) == len(sort[1][1]) :
        print("Top 2 results are equivalent !")
        return

    # If there is a winner, apply score trust gain to 'winners' and loss to 'losers'

    # This is independent from the node weigh, it is just the higher number of votes of the system
    winning_prediction = sort[0][0] 

    # Lower nodes confidence for losers
    for i in range(1, len(sort)) :

        for node_id in result[sort[i][0]] :

            node = nodes[node_id]

            # If the node send a wrong, minor answer, we lower the node weigh by the (amount of wrong prediction) * (prediction ranks)
            node["trust"] = (node["trust"] - (len(sort[i][1]) * i)/(nb_answers-1))

            node["trust"] = 0 if node["trust"] < 0 else node["trust"]

            # We also stash the balance of the loser by 10 * (number of prediction - number of current wrong prediction)
            stash_amount = (nb_answers - len(sort[i][1]) * 10) if node['stake'] > (nb_answers - len(sort[i][1]) * 10) else node['stake']
            node['stake'] -= stash_amount
            pool += stash_amount

            node["responses"] += 1

            print(f"New trust (-) value for node {node["user"]} : {node["trust"]}")

    # Increase nodes confidence for winners
    for node_id in result[winning_prediction] :

        node = nodes[node_id]

        # If the node send right (consensus) answer, we reevaluate the weight of the node based on it's current weight scaled over its number of participation
        # [ (node weigh * node participation) + (number of good predictions / number of total answers) ]  / (node participation + 1)
        node["trust"] = (node["trust"]*node["responses"] + len(sort[0][1])/nb_answers) / (node["responses"] + 1)

        node["responses"] += 1

        print(f"New trust (+) value for node {node["user"]} : {node["trust"]}")

        # We also equally distribute the pool among the winners
        node["stake"] += pool / len(sort[0][1])

    final_selection(sort)


def final_selection(sort : list) :
    """Final decision based on node weigh and balance

    Args:
        sort (list): previous sorted list of nodes answers
    """

    # For each responses, we calculate the weigh of the answers using node balances

    answer_weigh = []

    for i, answer in enumerate(sort) :

        answer_weigh.append((sort[i][0], 0))

        for node_id in answer[1] :

            node = nodes[node_id]

            answer_weigh[i] =  (sort[i][0], answer_weigh[i][1] + node['trust'] * node['stake'])

    # We sort the answer by final balance

    sorted_answer_balance = sorted(answer_weigh, key=lambda item : item[1], reverse=True)

    print(sorted_answer_balance)

    print('Final winning prediction :', sorted_answer_balance[0][0]  )



def update_balance() :
    """Insert a new row in the node balance tracking
    """

    new_balance = [] 

    for node in nodes :

        new_balance.append([node["id"], node["stake"]])

    # Add the current balance to the list
    balance.insert(0, new_balance)
        
def save_to_database() :
    """Export the data to the JSON database (nodes & balance history)
    """

    data : json = {
        "nodes" : nodes,
        "balance" : balance
    }

    with open('./API_Stash/database.json', 'w+') as db :

        db.writelines(json.dumps(data, indent=4))

def main() :

    apply_slash(get_nodes(get_user_input(AUTOMATED_INPUT)))

    # Then, we save the new balance of accounts and the new node statistics
    update_balance()
    save_to_database()


if __name__ == "__main__":
    main()