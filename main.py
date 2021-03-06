# coding=utf8

from csv import DictWriter
from dataframes import branches, carriers, orders, inventory, products, task_lists, \
    product_not_in_stock, MIN_MISSING_PRODUCT_TO_ALERT, MISSING_PRODUCT_FILE
from gui import ok_msg, yes_no_msg
from maps_utils import find_closest_branches
from time import sleep
import threading



BUZZER_BRANCH = 109
BUZZER_VALUES = [1, 3]
PICK_UP_STR = 'איסוף עצמי'
# TASKS_LOCK = threading.Lock()
# INVENTORY_LOCK = threading.Lock()


def organize_orders():
    """ goes through all orders in the DataFrame and handles each one of them
    in a separate thread. """
    active_threads = []
    for _, order in orders.iterrows():
        handle_order(order)
        # threading.Thread(target=handle_order, args=[order]).start()
    # while len(threading.enumerate()) > 1:
    #     sleep(5)


def handle_order(order):
    """ handle an order from a customer according to the flow diagram. """
    # print "new order"
    if not string_cmp(order.delivery, PICK_UP_STR):  # delivery is needed
        closest_branches = find_closest_branches(order['address'])
        delivery_branch = closest_branches[0]
        stock_branch = find_closest_branch_with_product(closest_branches, order['product_id'], order.amount)
        is_in_delivery_branch = False
        if stock_branch:
            if delivery_branch == stock_branch:  # product leaves from closest branch
                is_in_delivery_branch = True
                # print 'delivery from home branch!'
                assign_to_carrier(order, delivery_branch, to_customer=True)
                return
            else:
                # print 'planning routing...'
                plan_route(order, stock_branch, delivery_branch)
                return
        if not supplier_delivers_to_branch(order, delivery_branch):
            if not supplier_delivers_to_customer(order):
                if not buzzerable(order):
                    exceptional(order)
        # update product_not_in_stock list
        key = [delivery_branch, order['product_id']]
        found = False
        for key1, key2 in product_not_in_stock:
            # if key not in product_not_in_stock:
            if key1 == key[0] and key2 == key[1]:
                product_not_in_stock[(key1,key2)].append(product_not_in_stock[(key1,key2)] + 1)
                found = True
                break
        if not found:
            product_not_in_stock[(key[0], key[1])] = 1



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
    # print "in assign_to_carrier()"
    product_id = str(order.product_id)
    entry = {
        'dst_address': get_unicode(order['address']) if to_customer else (branches[branches['branch_id'] == args[0]].address.iloc[0]).encode('utf-8'),
        'product_id': product_id,
        'recipient': get_unicode(order['name']) if to_customer else (branches[branches['branch_id'] == args[0]].branch_name.iloc[0]).encode('utf-8'),
        'phone_number': order['phone_number'] if to_customer else (branches[branches['branch_id'] ==
                                                                           args[0]].phone_number.iloc[0]).encode('utf-8')
    }

    carrier_name = 'buzzer' if carrier_branch == BUZZER_BRANCH \
        else str(carriers.loc[carriers.branch_id == carrier_branch].branch_id.iloc[0])

    # TASKS_LOCK.acquire()
    task_lists[carrier_name].append(entry)
    # TASKS_LOCK.release()
    # print "TASKS_LOCK.release() from thread " + threading.current_thread().getName()
    # Update inventory
    if to_customer:
        # INVENTORY_LOCK.acquire()
        curr_val = inventory.loc[inventory.product_id == str(product_id)][str(carrier_branch)].iloc[0]
        inventory.set_value(str(product_id), str(carrier_branch), curr_val - order.amount)
        # INVENTORY_LOCK.release()


def plan_route(order, src_branch, dst_branch):
    """ a route passes from branch A to branch B and then directly to the customer. """
    assign_to_carrier(order, src_branch, False, dst_branch)
    assign_to_carrier(order, dst_branch)


def supplier_delivers_to_branch(order, branch_id):
    """ prompt the user to check if the relevant supplier can provide the product to the delivery
    branch. If it can - the relevant task is added to the delivery branch's list. """
    product_id = order.product_id
    supplier_name = products.loc[products.product_id == str(product_id)].supplier_name.iloc[0]
    product_name = products.loc[products.product_id == str(product_id)].product_name.iloc[0]
    branch_name = branches.loc[branches.branch_id == branch_id].branch_name.iloc[0]

    msg = 'Can supplier {} send product {} ({}) to branch {}?'.format(
            get_unicode(supplier_name), product_id, get_unicode(product_name), get_unicode(branch_name))
    # print msg
    res = yes_no_msg(msg)
    if res:
        assign_to_carrier(order, branch_id)
        return True
    return False

    # # with threads
    # user_response = ''
    # while user_response not in ['Y', 'N', 'y', 'n']:
    #     user_response = raw_input('Can supplier {} send product {} ({}) to branch {}?\tY/N\t'.format(
    #         get_unicode(supplier_name), product_id, get_unicode(product_name), get_unicode(branch_name)))
    # if user_response.lower() == 'y':
    #     assign_to_carrier(order, branch_id)
    #     return True
    # return False


def supplier_delivers_to_customer(order):
    """ prompt the user to check if the relevant supplier can provide the product directly
    to the customer. If it can - this is taken care of manually - no task is added to the lists. """
    product_id = order.product_id
    supplier_name = products.loc[products.product_id == str(product_id)].supplier_name.iloc[0]
    product_name = products.loc[products.product_id == str(product_id)].product_name.iloc[0]
    address = order.address

    msg = 'Can supplier {} send product {} ({}) to customer at address'
    '{}?\tY/N\t'.format(get_unicode(supplier_name), product_id, get_unicode(product_name),  get_unicode(address))
    print msg
    return yes_no_msg(msg)

    # # with threads
    # user_response = ''
    # while user_response not in ['Y', 'N', 'y', 'n']:
    #     user_response = raw_input('Can supplier {} send product {} ({}) to customer at address'
    #                               '{}?\tY/N\t'.format(get_unicode(supplier_name), product_id,
    #                                                   get_unicode(product_name),  get_unicode(address)))
    # return user_response.lower() == 'y'


def buzzerable(order):
    """ check if a product can be delivered by Buzzer. If it can - assign it correctly. """
    product_id = order.product_id
    buzzer_value = products.loc[products.product_id == str(product_id)].buzzerable.iloc[0]
    if buzzer_value in BUZZER_VALUES:
        assign_to_carrier(order)
        return True
    return False


def exceptional(order):
    """ prints an error regarding delivery failure. """
    msg = 'Exception: order {} to customer {} cannot be delivered.\n' \
          'Please inform the customer of this issue at {}'.format(order.order_id, order.name, order.phone_number)
    ok_msg(msg)



def create_missing_prod_file():
    inner_list = []
    for key in product_not_in_stock:
        prod_counter = product_not_in_stock[key]
        if prod_counter >= MIN_MISSING_PRODUCT_TO_ALERT:
            inner_list.append([key[0], key[1], prod_counter])

    for row in sorted(inner_list):
        with open(MISSING_PRODUCT_FILE, 'a') as f:
            value = (','.join(["%s" % val for val in row]))
            if str(type(value)) == 'unicode':
                value = value.encode('utf-8')
            f.write(value)
            f.write("\n")


def write_task_lists_to_file():
    print 'writing to file...'
    for carrier, tasks in task_lists.iteritems():
        if tasks:
            keys = tasks[0].keys()
            with open('{}.csv'.format(str(carrier)), "w") as f:
                dict_writer = DictWriter(f, keys, delimiter=",")
                dict_writer.writeheader()
                for task in tasks:
                    dict_writer.writerow(task)


if __name__ == '__main__':
    organize_orders()
    write_task_lists_to_file()
    # create_missing_prod_file()

