import pandas as pd


PATH = 'C:\Users\itc_user1\Desktop\HackIDC\Challenge\data'


# import branches
branches_headers = ['branch_id', 'district', 'address']
branches_cols = [0, 8, 11] # column indices
branches = pd.read_csv('{}/branches.csv'.format(PATH), encoding='hebrew', usecols=branches_cols,                      header=0, names=branches_headers)
branches.head(n=5)

# import orders
orders_headers = ['order_id', 'name', 'address', 'phone_number', 'date', 'product_id', 'amount', 'order_status']
orders_cols = [0, 1, 2, 3, 4, 5, 11 , 12] # column indices
orders = pd.read_csv('{}/orders.csv'.format(PATH), encoding='hebrew', usecols=orders_cols,                      header=0, names=orders_headers)
orders.head(n=5)

# import carriers
carriers_headers = ['branch_id', 'carrier_name']
carriers_cols = [0, 2] # column indices
carriers = pd.read_csv('{}/carriers.csv'.format(PATH), encoding='hebrew', usecols=carriers_cols,                      header=0, names=carriers_headers)
carriers.head(n=5)

# import inventory
exclude_cols = [1, 2, 3] # item description and total item count
exclude_rows = [0] # branches names
inventory = pd.read_csv('{}/inventory.csv'.format(PATH))
inventory.drop(inventory.columns[exclude_cols], axis=1, inplace=True)
inventory.drop(inventory.index[exclude_rows], axis=0, inplace=True)
inventory.head(5)



