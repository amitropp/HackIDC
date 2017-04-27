#coding=utf8

from dataframes import branches, carriers, orders, inventory, products


PICK_UP_STR = "איסוף עצמי"


def organize_orders():
    """ goes through all orders in the DataFrame and handles each one of them
    according to the flow diagram. """
    task_lists = initialize_task_lists()
    for _, order in orders.iterrows():
        if not string_cmp(order.delivery, PICK_UP_STR):  # delivery is needed
            product_id = order['product_id']
            customer_address = order['address']
            # print "product_id : " + product_id
            branches_ids_by_duration = find_closest_branch(customer_address)
            delivery_branch = branches_ids_by_duration[0]
            delivery_branch = 102 #haifa
            stock_branch = find_closest_branch_with_product(branches_ids_by_duration, prod_id=product_id)
            stock_branch = 112 #jerusalem
            if delivery_branch == stock_branch:  # product leaves from closest branch
                 assign_to_carrier(order, delivery_branch, task_lists, to_customer=True)
                 continue
            # delivery_branch_sidtrict = branches.loc[branches.branch_id == delivery_branch].district.iloc[0]
            # dstock_branch_sidtrict = branches.loc[branches.branch_id == stock_branch].district.iloc[0]
            # if string_cmp(delivery_branch_sidtrict, dstock_branch_sidtrict):  # product is in customer's district
            if stock_branch != -1:
                plan_route(order, stock_branch, delivery_branch)
                continue
            else:
                if not check_supplier_delivery_to_branch(order['product_id'], delivery_branch):
                    if not check_supplier_delivery_to_customer(order):
                        if not bazzerable(order):
                            exceptional()


def initialize_task_lists():
    """ initializes an empty list of tasks per each carrier in the carriers DataFrame. """
    return {carrier.carrier_name: [] for index, carrier in carriers.iterrows()}


def get_unicode(s):     #pass test
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return s


def string_cmp(str1, str2):     #pass test
    """ compares strings, including ones in Hebrew. """
    return get_unicode(str1) == get_unicode(str2)


def product_in_branch(product_id, branch_id): #pass test
    """ returns True iff the product is in the given branch's inventory. """
    return inventory.loc[inventory['product_id'] == str(product_id)][str(branch_id)].iloc[0] > 1


def find_closest_branch(customer_address):
    """ returns a list of Branches IDs sorted from the nearest to the farthest from the customer address."""
    # call tal's function
    return []


def find_closest_branch_with_product(branches_ids_by_duration, product_id):
    """ returns branch ID of the nearest branch with product in stock.
    return -1 if there is no relevant branch"""
    for id in branches_ids_by_duration:
        if product_in_branch(product_id, id):
            return id
    return -1

def assign_to_carrier(order, delivery_branch, task_lists, to_customer=True, *args): #pass test to_customer=True
    """ adds an entry to the delivery list of the correct carrier.
    args[0] is the branch ID to deliver to, in case of inter-branch delivery. """
    entry = {
        'dst_address': order['address'] if to_customer else branches[branches['branch_id'] == args[0]].address,
        'product_id': order['product_id'],
        'recipient': order['name'] if to_customer else branches[branches['branch_id'] == args[0]].branch_name,
        'phone_number': order['phone_number'] if to_customer else branches[branches['branch_id'] ==
                                                                           args[0]].phone_number
    }
    carrier_name = carriers.loc[carriers.branch_id == delivery_branch].carrier_name.iloc[0]
    task_lists[carrier_name].append(entry)


def plan_route(order, src_branch, dst_branch): # TODO implement
    pass


def check_supplier_delivery_to_branch(product_id, branch_id): # TODO implement
    pass


def check_supplier_delivery_to_customer(order): # TODO implement
    pass


def bazzerable(order): # TODO implement
    """Check if there ia """
    pass


def exceptional(): # TODO implement
    pass

if __name__ == '__main__':
    organize_orders()
