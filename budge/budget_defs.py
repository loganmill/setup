
# All time values (YEAR, MONTH, BUDGET_FREQ, 'span' values') are in seconds.

DAY = 24.0 * 60 * 60
WEEK = 7 * DAY
MONTH = DAY * 30
YEAR = 365 * DAY

# Define how often you run the budget app, always a multiple of DAY
BUDGET_FREQUENCY = DAY * 1

BUDGET = {
   'AMAZON':{
     'limit':0, 'span': WEEK},
   'Alcohol & Bars':{
      'limit':50, 'span': MONTH},
  'Auto Service':{
      'limit': 500 * 12, 'span': MONTH},
  'Books':{
      'limit': 100, 'span': MONTH},
  'Business (consultants, accountants)':{
      'limit': 28, 'span': MONTH},
  'Cash':{
      'limit': 150, 'span': MONTH},
  'Charity':{
      'limit':42, 'span': MONTH},
  'Clothing':{
      'limit':200, 'span': MONTH},
  'Counseling':{
      'limit':165, 'span': MONTH},
  'Dentist':{
      'limit': 470, 'span': MONTH},
  'Doctor':{
      'limit': 481,
      'span': MONTH},
  'Eye Doctor':{
      'limit': 100,
      'span': MONTH},
  'Drugstore':{
      'limit': 150, 'span': MONTH},
  'Energy, Gas & Electric':{
      'limit':217, 'span': MONTH},
  'Electronics & Software':{
      'limit':138, 'span': MONTH},
  'Entertainment':{
      'limit':148, 'span': MONTH},
  'Movies, DVDs & Music':{
      'limit': 160, 'span': MONTH},
  'Fast Food & Convenience':{
      'limit':168, 'span': MONTH},
  'Federal Tax':{
      'limit': 467, 'span': MONTH},
  'Gas & Fuel':{
      'limit':133, 'span': MONTH},
  'Gifts':{
      'limit':200, 'span': MONTH},
  'Groceries':{
      'limit':1400, 'span': MONTH},
  'Hair & Nails':{
      'limit':71, 'span': MONTH},
  'Home Improvement/Maintenance':{
      'limit':879, 'span': MONTH},
  'Insurance':{
      'limit': 262, 'span': MONTH},
  'Interest Income':{
      'limit': 0, 'span': MONTH},
  'Income':{
      'limit': 0, 'span': MONTH},
  'Investment Savings':{
      'limit': 0, 'span': MONTH},
  'Kids':{
      'limit': 1500, 'span': MONTH},
  'Merchandise/Misc':{
      'limit': 361, 'span': MONTH},
  'Mortgage':{
      'limit':4373, 'span': MONTH},
  'Movies & Music':{
      'limit':0, 'span': MONTH},
  'Restaurants/Dining':{
      'limit':0, 'span': MONTH},
  'Parental Travel':{
      'limit':200, 'span':MONTH},
  'Parking & Tolls':{
      'limit':78, 'span': MONTH},
  'Pets':{
      'limit':74,   'span': MONTH},
  'Phone, Internet & Cable':{
      'limit':382, 'span': MONTH},
  'Public Transport':{
      'limit':19, 'span': MONTH},
  'Restaurants/Dining':{
      'limit':250, 'span': MONTH},
  'Service Fee':{
      'limit':10, 'span': MONTH},
  'Shipping & Handling':{
      'limit': 34, 'span': MONTH},
  'Sports & Hobbies':{
      'limit': 143, 'span': MONTH},
  'State Tax':{
      'limit': 0, 'span': MONTH},
  'Tax preparation':{
      'limit': 72, 'span': MONTH},
  'Travel & Vacation':{
      'limit':500, 'span': MONTH},
  'Veterinary':{
      'limit':75, 'span': MONTH},
  'Water':{
      'limit':141, 'span': MONTH},
   # unbudgeted catefories from emoney:
  'Rental Car':{
      'limit':0, 'span': MONTH},
  'Credit Card Payment':{
      'limit':0, 'span': MONTH},
  'Income':{
      'limit':0, 'span': MONTH}
}
  
  
