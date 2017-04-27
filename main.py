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
            # delivery_branch = find_closest_branch(customer_address)
            delivery_branch = 102 #haifa
            # stock_branch = find_closest_branch(customer_address, prod_id=product_id)
            stock_branch = 112 #jerusalem
            if delivery_branch == stock_branch:  # product leaves from closest branch
                 assign_to_carrier(order, delivery_branch, task_lists, to_customer=True)
                 continue
            delivery_branch_sidtrict = branches.loc[branches.branch_id == delivery_branch].district.iloc[0]
            dstock_branch_sidtrict = branches.loc[branches.branch_id == stock_branch].district.iloc[0]
            if string_cmp(delivery_branch_sidtrict, dstock_branch_sidtrict):  # product is in customer's district
                print "delivery_branch_sidtrict == dstock_branch_sidtrict"
                plan_route(order, stock_branch, delivery_branch) #TODO test
                continue
            else:
                print "delivery_branch_sidtrict != dstock_branch_sidtrict"
                # if not check_supplier_delivery_to_branch(order['product_id'], delivery_branch):
                #     if not check_supplier_delivery_to_customer(order):
                #         if not bazzerable(order):
                #             exceptional()


def initialize_task_lists():
    """ initializes an empty list of tasks per each carrier in the carriers DataFrame. """
    return {carrier.carrier_name: [] for index, carrier in carriers.iterrows()}


def get_unicode(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return s


def string_cmp(str1, str2):
    """ compares strings, including ones in Hebrew. """
    return get_unicode(str1) == get_unicode(str2)


def product_in_branch(product_id, branch_id):
    """ returns True iff the product is in the given branch's inventory. """
    prod_entry = inventory[inventory['product_id'] == product_id]
    return prod_entry[branch_id] > 1


def find_closest_location(locations, address):  # TODO implement
    """ returns the ID of the closest branch out of a list using the GoogleMaps API. """
    return locations and address


def find_closest_branch(customer_address, prod_id=None):
    """ returns the branch ID of the branch which is closest to the customer address.
    if a product ID is given - the returned branch must have the required product. """
    if not prod_id:
        branches_locations = [branch['branch_id'] for branch in branches]  # closest branch to customer
    else:  # closest branch to customer with the given product
        branches_locations = [branch['branch_id'] for branch in branches
                              if product_in_branch(prod_id, branch['branch_id'])]
    closest_branch = find_closest_location(branches_locations, customer_address)
    return closest_branch


def find_close_branch_with_product(customer_address, product_id):
    pass


def assign_to_carrier(order, delivery_branch, task_lists, to_customer=True, *args):
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


def plan_route(order, src_branch, dst_branch):
    pass


def check_supplier_delivery_to_branch(product_id, branch_id):
    pass


def check_supplier_delivery_to_customer(order):
    pass


def bazzerable(order):
    pass


def exceptional():
    pass

if __name__ == '__main__':
    organize_orders()
