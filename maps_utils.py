import requests
from dataframes import branches

FILE_NAME = "branches_distances.csv"
# The maximum duration travel we are allowing from out source to the destination
MAX_DURATION = 1800


our_key = "AIzaSyAl6XMzwkqP4FQn_RDIE0XP6WyyoG2ah_g"
url = "https://maps.googleapis.com/maps/api/distancematrix/json" + \
      "?units=imperial" + "&origins={0}&destinations={1}&key=" + our_key


def get_unicode(s):  # pass test
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return s


def find_closest_branches(customer_address):
    """ This function returns a list of branche's ids in ascending order by their distance from the costumer"""
    # If the duration travel is less than the maximum - add it to the list
    # The branche's ids that are in the transport distance
    relevant_branches = []
    min_duration = float('Inf')
    min_id = -1
    branches_array = []

    for idx, branch in branches.iterrows():
        address = branch.address
        curr_url = url.format(get_unicode(address), get_unicode(customer_address))

        # Convert to json format
        response = requests.get(curr_url).json()
        # print 'response', response

        # Return the duration time from the origin to destination (in seconds)
        curr_dur = response["rows"][0]["elements"][0]["duration"]["value"]
        curr_id = branch.branch_id
        branches_array += [(curr_id, curr_dur)]

        if min_duration > curr_dur:
            min_duration = curr_dur
            min_id = curr_id

    # sort the array by duration
    sorted_list = sorted(branches_array, key=lambda x: x[1])

    for i in range(len(sorted_list)):
        if sorted_list[i][1] <= MAX_DURATION:
            relevant_branches.append(sorted_list[i][0])
        # In case that the closet branch to the customer farthest from the MAX_DURATION - return the specific branch
        elif min_duration > MAX_DURATION:
            return [min_id]
        else:
            break
    return relevant_branches




def tal_test2():


    product_not_in_stock ={}
    product_not_in_stock["stock_d", 5] = 2
    product_not_in_stock["stock_a", 1] = 1
    product_not_in_stock["stock_b", 1] = 4
    product_not_in_stock["stock_c", 1] = 21
    product_not_in_stock["stock_a", 2] = 3
    product_not_in_stock["stock_j", 101] = 1
    product_not_in_stock["stock_a", 3] = 12
    product_not_in_stock["stock_j", 100] = 10


    MIN_MISSING_PRODUCT = 1
    inner_list = []
    for key in product_not_in_stock:
        prod_counter = product_not_in_stock[key]
        if prod_counter >= MIN_MISSING_PRODUCT:
            inner_list += [key, prod_counter]
            # if prod_counter < MIN_MISSING_PRODUCT:
            #     del product_not_in_stock[key]
    print("fin")
    # Sort the list by branches
    sortted_list = sorted(inner_list[0][0])
    # now = datetime.datetime.now()
    file_name = "mis_prod_.csv"

    for row in sortted_list:

        print(row)
        # with open(file_name, 'a') as f:
        #     f.write((','.join(["%s" % val for val in row])))
        #     f.write("\n")
            # line = open("branches_distances.csv","r").readline()
    print("fin")