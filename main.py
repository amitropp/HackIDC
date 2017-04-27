#coding=utf8

PICK_UP_STR= "איסוף עצמי"

def compare_hebrew(str1, str2):
    return str1.decode('UTF-8') == str2.decode('UTF-8')


#main function
def organize_orders(orders):
    # initialize carriers lists
    for order in orders:
        #if need delivery
        if not compare_hebrew(order['delivery'], PICK_UP_STR):
            delivery_branch = extract_closest_branch()
            stock_branch = find_close_branch_with_product()
            # prudoct exit at the delivery branch
            if delivery_branch == stock_branch:
                assign_to_carrier(order, delivery_branch)
                continue
            if compare_hebrew(delivery_branch['district'], stock_branch['district']):
                #found product on the same district
                plan_route(order, stock_branch, delivery_branch)
                continue
            else:
                if not check_supplier_delivery_to_branch(order['product_id'], delivery_branch):
                    if not check_supplier_delivery_to_customer(order):
                        if not bazzerable(order):
                            exceptional()



#return branch id
def extract_closest_branch(customer_address):
    pass

#return branch id
def find_close_branch_with_product(customer_address, product_id):
    pass

#optional args - branch_id to deliver to
def assign_to_carrier(order, delivery_branch_id, to_customer=True, *args):
    pass


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

