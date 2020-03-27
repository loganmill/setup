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
AMAZON_EXCEPTIONS_PATH = os.path.expanduser('~/.amazon_exceptions.json')

# Define end date of budget, usually 'now'.
# today() is equivalent to date.fromtimestamp(time.time())
# Examples:
# datetime.datetime.today()
# datetime.datetime.strptime('2019-11-19, DATE_FORMAT) 
# datetime.datetime.fromisoformat('2019-11-19')
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# Define how often you run the budget app, in days.
# This creates how much 'free space' you have for an item.
BUDGET_FREQUENCY = 0  # Normally 1 day

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
      'limit':300, 'span': MONTH * 3},
  'Auto Service':{
      'limit': 500 * 6, 'span': MONTH * 6},
  'Books':{
      'limit': 47*3, 'span': MONTH * 3},
  'Business (consultants, accountants)':{
      'limit': 45 * 6, 'span': MONTH * 6},
  'Cash/ATM':{
      'limit': 200, 'span': MONTH*3},
  'Charity':{
      'limit':500, 'span': MONTH * 6},
  'Clothing':{
      'limit':75 * 6, 'span': MONTH * 6},
  'Counseling':{
      'limit':165, 'span': MONTH},
  'Dentist':{
      'limit': 2400, 'span': MONTH * 6},
  'Doctor':{
      'limit': 3230,
      'span': MONTH * 6},
  'Eye Doctor':{
      'limit': 250,
      'span': MONTH * 6},
  'Drugstore':{
      'limit': 130, 'span': MONTH},
  'Energy, Gas & Electric':{
      'limit':217, 'span': MONTH},
  'Electronics & Software':{
      'limit':150*4, 'span': MONTH*4},
  'Entertainment':{
      'limit':130, 'span': MONTH},
  'Movies, DVDs & Music':{
      'limit': 135, 'span': MONTH},
  'Fast Food & Convenience':{
      'limit':168, 'span': MONTH},
  'Federal Tax':{
      'limit': 0, 'span': MONTH},
  'Gas & Fuel':{
      'limit':140, 'span': MONTH},
  'Gifts':{
      'limit':360, 'span': MONTH},
  'Groceries':{
      'limit':1400, 'span': MONTH},
  'Hair & Nails':{
      'limit':79 * 2, 'span': MONTH * 2},
  'Home Improvement/Maintenance':{
      'limit':879*6, 'span': MONTH*6},
  'Insurance':{
      'limit': 270*6, 'span': MONTH*6},
  'Interest Income':{
      'limit': 0, 'span': MONTH},
  'Income':{
      'limit': 0, 'span': MONTH},
  'Investment Savings':{
      'limit': 0, 'span': MONTH},
  'Kids':{
      'limit': 1400*4, 'span': MONTH*4},
  #'Merchandise/Misc':{
  #    'limit': 361, 'span': MONTH},
  'Mortgage':{
      'limit':4373, 'span': MONTH},
  'Movies & Music':{
      'limit':135, 'span': MONTH},
  'Restaurants/Dining':{
      'limit':200*3, 'span': MONTH*3},
  'Parental Travel':{
      'limit':200*3, 'span':MONTH*3},
  'Parking & Tolls':{
      'limit':78, 'span': MONTH},
  'Pets':{
      'limit':44*3,   'span': MONTH*3},
  'Phone, Internet & Cable':{
      'limit':382, 'span': MONTH},
  'Public Transport':{
      'limit':19, 'span': MONTH},
  'Restaurants/Dining':{
      'limit':200*3, 'span': MONTH*3},
  'Service Fee':{
      'limit':10, 'span': MONTH},
  'Shipping & Handling':{
      'limit': 21, 'span': MONTH},
  'Sports & Hobbies':{
      'limit': 70*6, 'span': MONTH*6},
  'State Tax':{
      'limit': 0, 'span': MONTH},
  'Tax preparation':{
      'limit': 72*12, 'span': YEAR},
  'Travel & Vacation':{
      'limit':300*6, 'span': MONTH*6},
  'Unclassified':{
      'limit':0, 'span':MONTH*4},
  'Veterinary':{
      'limit':55*6, 'span': MONTH*6},
  'Water':{
      'limit':200, 'span': MONTH},
   # unbudgeted categories from emoney:
  'Rental Car':{
      'limit':0, 'span': MONTH},
  'Credit Card Payment':{
      'limit':0, 'span': MONTH},
  'Income':{
      'limit':0, 'span': MONTH}
}
  
  
AMAZON_CATEGORIES = {
    'OUTDOOR_RECREATION_PRODUCT':'Sports & Hobbies',
    'SPORTING_GOODS':'Sports & Hobbies',
    'ABIS_BOOK': 'Gifts',
    'BEAUTY':'Drugstore',
    'GROCERY':'Groceries',
    'CELLULAR_PHONE_CASE':'Electronics & Software',
    'HEADPHONES':'Electronics & Software',
    'CABLE_OR_ADAPTER':'Electronics & Software',        
    'CHARGING_ADAPTER':'Electronics & Software',        
    'CONSUMER_ELECTRONICS':'Electronics & Software',
    'SPEAKERS':'Electronics & Software',
    'STICKER_DECAL':'Electronics & Software',
    'BACKPACK':'Sports & Hobbies',                
    'PANTS':'Clothing',
    'HOME':'Home Improvement/Maintenance',
    'OUTDOOR_LIVING':'Home Improvement/Maintenance',
    'HOME_LIGHTING_AND_LAMPS':'Gifts',
    'LUGGAGE':'Travel & Vacation',    
    'TEA':'Groceries',
    'PANTRY':'Groceries',
    'WALLET':'Clothing',
    'PET_FOOD':'Pets',
    'PERSONAL_COMPUTER':'Electronics & Software',
    'HEALTH_PERSONAL_CARE':'Drugstore',
    'LAB_SUPPLY':'Drugstore',
    'PERSONAL_CARE_APPLIANCE':'Drugstore',
    'TUNER':'Electronics & Software',
    'KITCHEN':'Home Improvement/Maintenance',
    'HARDWARE':'Home Improvement/Maintenance',
    'ELECTRONIC_ADAPTER':'Electronics & Software',
    'ELECTRONIC_COMPONENT':'Electronics & Software',
    'POWER_SUPPLIES_OR_PROTECTION':'Electronics & Software',
    'WIRELESS_ACCESSORY':'Electronics & Software',
    'TOOLS':'Home Improvement/Maintenance'
}
