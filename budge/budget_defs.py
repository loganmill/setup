from collections import namedtuple
import datetime
import os
import sys

DATE_FORMAT = '%Y-%m-%d'

# All time values (YEAR, MONTH, BUDGET_FREQ, 'span' values') are in days.

DAY = 1
WEEK = 7 * DAY
MONTH = DAY * 30
THREE_MONTHS = MONTH * 3
SIX_MONTHS = MONTH * 6
YEAR = 365 * DAY

# For testing:
#THREE_MONTHS = SIX_MONTHS = YEAR = MONTH

BUDGET_DIR = os.path.expanduser('~/.budget')
BUDGET_DIR = os.path.abspath(BUDGET_DIR)        

CONFIG_PATH = os.path.join(BUDGET_DIR, 'config.json')
EMONEY_CACHE_PATH = os.path.join(BUDGET_DIR, 'emoney_cache.json')
AMAZON_CACHE_PATH = os.path.join(BUDGET_DIR,'amazon_cache.json')
AMAZON_EXCEPTIONS_PATH = os.path.join(BUDGET_DIR, 'amazon_exceptions.json')
ARCHIVE_DIR = os.path.join(BUDGET_DIR, 'archive/')
REPORTS_DIR = os.path.join(BUDGET_DIR, 'reports/')

if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)



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
   #'Stepper':{
   #  'limit':0, 'span': 12*MONTH},
   'Unknown Amazon':{
     'limit':0, 'span': MONTH},
   'Unknown Emoney':{
     'limit':0, 'span': MONTH},
   'Alcohol & Bars':{
      'limit':300, 'span': THREE_MONTHS},
  'Auto Service':{
      'limit': 500 * 12, 'span': YEAR},
  'Books':{
      'limit': 47*3, 'span': THREE_MONTHS},
  'Business (consultants, accountants)':{
      'limit': 45 * 6, 'span': SIX_MONTHS},
  'Cash/ATM':{
      'limit': 200, 'span':THREE_MONTHS},
  'Charity':{
      'limit':500, 'span': SIX_MONTHS},
  'Clothing':{
      'limit':75 * 6, 'span': SIX_MONTHS},
  'Counseling':{
      'limit':165, 'span': MONTH},
  'Dentist':{
      'limit': 2400, 'span': SIX_MONTHS},
  'Doctor':{
      'limit': 3230, 'span': SIX_MONTHS},
  'Eye Doctor':{
      'limit': 250, 'span': SIX_MONTHS},
  'Drugstore':{
      'limit': 130, 'span': MONTH},
  'Energy, Gas & Electric':{
      'limit':217, 'span': MONTH},
  'Electronics & Software':{
      'limit':150*6, 'span': SIX_MONTHS},
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
      'limit':79 * 3, 'span': THREE_MONTHS},
  'Home Improvement/Maintenance':{
      'limit':879*6, 'span': SIX_MONTHS},
  'Insurance':{
      'limit': 270*6, 'span': SIX_MONTHS},
  'Interest Income':{
      'limit': 0, 'span': MONTH},
  'Income':{
      'limit': 0, 'span': MONTH},
  'Investment Savings':{
      'limit': 0, 'span': MONTH},
  'Kids':{
      'limit': 1400*3, 'span': THREE_MONTHS},
  #'Merchandise/Misc':{
  #    'limit': 361, 'span': MONTH},
  'Mortgage':{
      'limit':4373, 'span': MONTH},
  'Movies & Music':{
      'limit':135, 'span': MONTH},
  'Restaurants/Dining':{
      'limit':200*3, 'span': THREE_MONTHS},
  'Parental Travel':{
      'limit':200*3, 'span':THREE_MONTHS},
  'Parking & Tolls':{
      'limit':78, 'span': MONTH},
  'Pets':{
      'limit':44*3,   'span': THREE_MONTHS},
  'Phone, Internet & Cable':{
      'limit':382, 'span': MONTH},
  'Public Transport':{
      'limit':19, 'span': MONTH},
  'Restaurants/Dining':{
      'limit':200*3, 'span': THREE_MONTHS},
  'Service Fee':{
      'limit':10, 'span': MONTH},
  'Shipping & Handling':{
      'limit': 21, 'span': MONTH},
  'Sports & Hobbies':{
      'limit': 70*6, 'span': SIX_MONTHS},
  'State Tax':{
      'limit': 0, 'span': MONTH},
  'Tax preparation':{
      'limit': 72*12, 'span': YEAR},
  'Travel & Vacation':{
      'limit':300*6, 'span': SIX_MONTHS},
  'Unclassified':{    # this could be excluded from budget totals...includes money transfer
      'limit':0, 'span':MONTH},
  'Veterinary':{
      'limit':55*6, 'span': SIX_MONTHS},
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
