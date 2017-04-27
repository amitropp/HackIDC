import requests, math
from dataframes import branches, carriers, orders, inventory, products

FILE_NAME = "branches_distances.csv"
# The maximum duration travel we are allowing from out source to the destination
MAX_DURATION = "9000"


our_key = "AIzaSyABeegXYIuVyyLT78Xzj2jFbcYH1iL45UM"
url = "https://maps.googleapis.com/maps/api/distancematrix/json" + \
      "?units=imperial" + "&origins={0}&destinations={1}&key=" + our_key

def writeToFile(row):
    with open(FILE_NAME, 'a') as f:
        f.write(row)
        f.write("\n")


# Calc the distance
def calcDisFromBranches(branches):

    for idx, branch in enumerate(branches):
        # Create an empty array for the durations
        durArray = [0] * len(branches)
        for innerIdx, des in enumerate(branches):

            if idx != innerIdx:
                curr_url = url.format(branch, des)

                # Convert to json format
                print("calc dis from: " + branch + "to ==  " + des)
                response = requests.get(curr_url).json()

                # Return the duration time from the origin to destination (in seconds)
                print(response)
                durArray[innerIdx] = response["rows"][0]["elements"][0]["duration"]["value"]
        # For each row writes to the csv file the distances from the origin
        writeToFile(','.join(["%d" % val for val in durArray]))


def find_closest_branch(customer_address):
    """ This function returns a list of branche's ids in ascending order"""
    # If the duration travel is less than the maximum - add it to the list
    relavant_branches = []
    for _, branch in branches.iterrows():
        min_duration = math.inf
        min_id = -1

        addres = branch.address
        id = branch.branch_id

        curr_url = url.format(addres, customer_address)

        # Convert to json format
        print("calc dis from: " + branch + "to ==  " + customer_address)
        response = requests.get(curr_url).json()

        # Return the duration time from the origin to destination (in seconds)
        print(response)
        durArray[innerIdx] = response["rows"][0]["elements"][0]["duration"]["value"]
        # For each row writes to the csv file the distances from the origin
        writeToFile(','.join(["%d" % val for val in durArray]))
