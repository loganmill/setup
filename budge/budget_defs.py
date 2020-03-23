from collections import namedtuple
import datetime
import os

DATE_FORMAT = '%Y-%m-%d'

# All time values (YEAR, MONTH, BUDGET_FREQ, 'span' values') are in days.

DAY = 1
WEEK = 7 * DAY
MONTH = DAY * 30
YEAR = 365 * DAY

CONFIG_PATH = os.path.expanduser('~/.budget_config.json')
EMONEY_CACHE_PATH = os.path.expanduser('~/.emoney_cache.json')
AMAZON_CACHE_PATH = os.path.expanduser('~/.amazon_cache.json')

# Define end date of budget, usually 'now'.
# today() is equivalent to date.fromtimestamp(time.time())
# Examples:
# datetime.datetime.today()
# datetime.datetime.strptime('2019-11-19, DATE_FORMAT) 
# datetime.datetime.fromisoformat('2019-11-19')
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# Define how often you run the budget app, in days.
# This creates how much 'free space' you have for an item.
BUDGET_FREQUENCY = 1  # Normally 1 day

# Define how many days of cache to 'invalidate', as more recent
# items in emoney (amazon?) can change for up to 3 weeks after their
# posted date. 
UNCACHE =  0 # Normally 21 days

BUDGET = {
   'Unknown Amazon':{
     'limit':0, 'span': MONTH},
   'Unknown Emoney':{
     'limit':0, 'span': MONTH},
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
  
  
AMAZON_CATEGORIES = {
    'OUTDOOR_RECREATION_PRODUCT':'Sports & Hobbies',
    'BEAUTY':'Merchandise/Misc',
    'PERSONAL_COMPUTER':'Electronics & Software',
    'TUNER':'Electronics & Software',
    'HARDWARE':'Home Improvement/Maintenance',
    'ELECTRONIC_COMPONENT':'Electronics & Software',
    'POWER_SUPPLIES_OR_PROTECTION':'Electronics & Software',
    'WIRELESS_ACCESSORY':'Electronics & Software',
    'TOOLS':'Home Improvement/Maintenance'
}
