# coding=utf8

from csv import DictWriter
from dataframes import branches, carriers, orders, inventory, products, task_lists, product_not_in_stock, MIN_MISSING_PRODUCT
from maps_utils import find_closest_branch
import datetime

BUZZER_BRANCH = 109
BUZZER_VALUES = [1, 3]
PICK_UP_STR = "איסוף עצמי"




def organize_orders():
    """ goes through all orders in the DataFrame and handles each one of them
    according to the flow diagram. """

    for _, order in orders.iterrows():
        if not string_cmp(order.delivery, PICK_UP_STR):  # delivery is needed
            product_id = order['product_id']
            customer_address = order['address']
            branches_ids_by_duration = find_closest_branch(customer_address)
            delivery_branch = branches_ids_by_duration[0]
            stock_branch = find_closest_branch_with_product(branches_ids_by_duration, product_id, order.amount)
            print 'delivery_branch : ' + str(delivery_branch)
            print 'stock_branch : ' + str(stock_branch)
            if stock_branch:
                if delivery_branch == stock_branch:  # product leaves from closest branch
                    print 'stock equals delivery'
                    assign_to_carrier(order, delivery_branch, to_customer=True)
                    continue
                else:
                    # Add to the list of missing products - the product that is related to this branch
                    key = [delivery_branch, product_id ]
                    if key in product_not_in_stock:
                        product_not_in_stock[key] +=1
                    else:
                        product_not_in_stock[key] = 1
                    print 'plans route'
                    plan_route(order, stock_branch, delivery_branch)
                    continue
            else:
                if not check_supplier_delivery_to_branch(order, delivery_branch):
                    if not check_supplier_delivery_to_customer(order):
                        if not buzzerable(order):
                            exceptional(order)
    #write_task_lists_to_file()


def get_unicode(s):  # pass test
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return s


def string_cmp(str1, str2):  # pass test
    """ compares strings, including ones in Hebrew. """
    return get_unicode(str1) == get_unicode(str2)


def product_in_branch(product_id, branch_id, amount):  # pass test
    """ returns True iff the product is in the given branch's inventory. """
    return inventory.loc[inventory.product_id == str(product_id)][str(branch_id)].iloc[0] >= 1 + amount


def find_closest_branch_with_product(branches_ids_by_duration, product_id, amount):
    """ returns branch ID of the nearest branch with product in stock or None if no such exists """
    for branch_id in branches_ids_by_duration:
        if product_in_branch(product_id, branch_id, amount):
            return branch_id
    return


def assign_to_carrier(order, carrier_branch=BUZZER_BRANCH, to_customer=True, *args):  # pass test to_customer=True
    """ adds an entry to the delivery list of the correct carrier.
    args[0] is the branch ID to deliver to, in case of inter-branch delivery. """
    entry = {
        'dst_address': get_unicode(order['address']) if to_customer else branches[branches['branch_id'] == args[0]].address,
        'product_id': order['product_id'],
        'recipient': get_unicode(order['name']) if to_customer else branches[branches['branch_id'] == args[0]].branch_name,
        'phone_number': order['phone_number'] if to_customer else branches[branches['branch_id'] ==
                                                                           args[0]].phone_number
    }
    carrier_name = 'buzzer' if carrier_branch == BUZZER_BRANCH \
        else carriers.loc[carriers.branch_id == carrier_branch].carrier_name.iloc[0]
    # print "type of : " + str(type(carrier_name))
    # print "carrier_name : " + carrier_name
    task_lists[carrier_name].append(entry)


def plan_route(order, src_branch, dst_branch):
    """ a route passes from branch A to branch B and then directly to the customer. """
    assign_to_carrier(order, src_branch, False, dst_branch)
    assign_to_carrier(order, dst_branch)


def check_supplier_delivery_to_branch(order, branch_id):
    """ prompt the user to check if the relevant supplier can provide the product to the delivery
    branch. If it can - the relevant task is added to the delivery branch's list. """
    product_id = order.product_id
    supplier_name = products.loc[products.product_id == str(product_id)].supplier_name.iloc[0]
    product_name = products.loc[products.product_id == str(product_id)].product_name.iloc[0]
    branch_name = branches.loc[branches.branch_id == branch_id].branch_name.iloc[0]

    user_response = ''
    while user_response not in ['Y', 'N', 'y', 'n']:
        user_response = raw_input('Can supplier {} send product {} ({}) to branch {}?\tY/N\t'.format(
            get_unicode(supplier_name), product_id, get_unicode(product_name), get_unicode(branch_name)))
    if user_response.lower() == 'y':
        assign_to_carrier(order, branch_id)
        return True
    else:
        return False


def check_supplier_delivery_to_customer(order):
    """ prompt the user to check if the relevant supplier can provide the product directly
    to the customer. If it can - this is taken care of manually - no task is added to the lists. """
    product_id = order.product_id
    supplier_name = products.loc[products.product_id == str(product_id)].supplier_name.iloc[0]
    product_name = products.loc[products.product_id == str(product_id)].product_name.iloc[0]
    address = order.address

    user_response = ''
    while user_response not in ['Y', 'N', 'y', 'n']:
        user_response = raw_input('Can supplier {} send product {} ({}) to customer at address'
                                  '{}?\tY/N\t'.format(get_unicode(supplier_name), product_id,
                                                      get_unicode(product_name),  get_unicode(address)))
    return user_response.lower() == 'y'


def buzzerable(order):
    """ check if a product can be delivered by Buzzer. If it can - assign it correctly. """
    product_id = order.product_id
    buzzer_value = products.loc[products.product_id == str(product_id)].buzzerable.iloc[0]
    if buzzer_value in BUZZER_VALUES:
        assign_to_carrier(order)
        return True
    return False


def exceptional(order):
    print 'Exception: order {} to customer {} cannot be delivered.\n' \
          'Please inform the customer of this issue at {}'.format(order.order_id, order.name, order.phone_number)


def write_task_lists_to_file():
    print 'writing to file...'
    for carrier, tasks in task_lists.iteritems():
        print type(carrier)
        if tasks:
            keys = tasks[0].keys()
            with open('{}.txt'.format(str(carrier)), "w") as f:
                dict_writer = DictWriter(f, keys, delimiter="\t")
                dict_writer.writeheader()
                for task in tasks:
                    dict_writer.writerow(task)


def create_missing_prod_file():

    inner_list = []
    for key in product_not_in_stock:
        prod_counter = product_not_in_stock[key]
        if prod_counter >= MIN_MISSING_PRODUCT:
            inner_list += [key, prod_counter]
        # if prod_counter < MIN_MISSING_PRODUCT:
        #     del product_not_in_stock[key]

    # Sort the list by branches
    sortted_list = sorted(inner_list[0][0])
    now = datetime.datetime.now()
    file_name = "mis_prod_" + str(now.date) + ".csv"

    for row in sortted_list:
        with open(file_name, 'a') as f:
            f.write((','.join(["%s" % val for val in row])))
            f.write("\n")
    # line = open("branches_distances.csv","r").readline()



def tal_test():

    print("fin")

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

    # Sort the list by branches
    sortted_list = sorted(inner_list[0][0])
    now = datetime.datetime.now()
    file_name = "mis_prod_" + str(now.date) + ".csv"

    for row in sortted_list:
        with open(file_name, 'a') as f:
            f.write((','.join(["%s" % val for val in row])))
            f.write("\n")
            # line = open("branches_distances.csv","r").readline()



if __name__ == '__main__':
    # organize_orders()

    tal_test()
