import pandas as pd


# PATH = 'C:\Users\itc_user1\Desktop\HackIDC\data'
PATH = '/Users/amitropp/Documents/Private/HackIDC/data'

# import branches
branches_headers = ['branch_id', 'branch_name', 'phone_number', 'district', 'address']
branches_cols = [0, 1, 6, 8, 11]  # column indices
branches = pd.read_csv('{}/branches.csv'.format(PATH), encoding='hebrew', usecols=branches_cols,
                       header=0, names=branches_headers)
branches.head(n=5)

# import orders
orders_headers = ['order_id', 'name', 'address', 'phone_number', 'date', 'product_id', 'delivery', 'amount', 'order_status']
orders_cols = [0, 1, 2, 3, 4, 5, 10, 11, 12] # column indices
orders = pd.read_csv('{}/orders.csv'.format(PATH), encoding='hebrew', usecols=orders_cols,
                     header=0, names=orders_headers)

# import carriers
carriers_headers = ['branch_id', 'carrier_name']
carriers_cols = [0, 2] # column indices
carriers = pd.read_csv('{}/carriers.csv'.format(PATH), encoding='hebrew', usecols=carriers_cols,
                       header=0, names=carriers_headers)

# import products
products_headers = ['product_id', 'supplier_id', 'supplier_name', 'buzzerable']
products_cols = [0, 2, 3, 4] # column indices
products = pd.read_csv('{}/products.csv'.format(PATH), encoding='hebrew', usecols=products_cols,
                       header=0, names=products_headers)

# import inventory
exclude_cols = [1, 2, 3] # item description and total item count
exclude_rows = [0] # branches names
inventory = pd.read_csv('{}/inventory.csv'.format(PATH))
inventory.drop(inventory.columns[exclude_cols], axis=1, inplace=True)
inventory.drop(inventory.index[exclude_rows], axis=0, inplace=True)


# initialize task lists
""" initializes an empty list of tasks per each carrier in the carriers DataFrame. """
task_lists = {carrier.carrier_name: [] for index, carrier in carriers.iterrows()}
task_lists['buzzer'] = []


