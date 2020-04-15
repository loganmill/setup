#!/usr/bin/env python3
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import copy
import json
import pdb
from re import sub

from budget_defs import *

# Only the following keys will be extracted from corresponding cache:
AMAZON_EXPENSE_KEYS = ['Date', 'Cost', 'Title', 'Category', 'Shipping Address City','Buyer Name',  'Source', 'Order ID']
EMONEY_EXPENSE_KEYS = ['Date', 'Cost', 'Description', 'Account', 'Category', 'Source', 'Order ID']
# Following merges previous 2: used for ordering on-screen presentation
EXPENSE_KEYS = ['Date', 'Cost', 'Title', 'Description', 'Category', 'Account', 'Shipping Address City', 'Buyer Name', 'Source', 'Order ID']

class CategoryExpenses(ModalView):

     current = None

     def __init__(self, details, *args, **kwargs):
         super(CategoryExpenses, self).__init__(*args, **kwargs)        
         CategoryExpenses.current = self
         self.details = details
         expenses = details['expenses']
         expenses.sort(reverse=True, key=lambda expense: str(expense['Date']))
         expense_list = self.ids['expense_list']
         for expense in expenses:
             expense_list.add_widget(Expense(expense))
         self.set_heading()

     def set_heading(self):
         details = self.details
         self.ids['heading'].text = '{}: {:.2f}/{:.2f} {} days'.format(
             details['category'], details['total'], details['limit'], details['span'])

class CategoryRow(ButtonBehavior,BoxLayout):

    # Warning: class vars don't work as expected when using RecycleViews:
    # the class can seemingly be reloaded during scrolling, causing apparent
    # reinitialization of class vars.
    details = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super(CategoryRow, self).__init__(*args, **kwargs)

    def on_details(self, row, details):
        if not details:
            return
        self.details = details
        #print(self.details['category'], self.details['total'])
        self.details['total'] = sum([expense['Cost'] for expense in details['expenses']])
        #print(self.details['category'], self.details['total'])
        self.over_budget = self.details['total'] > self.details['limit']
        for key,val in self.details.items():
            if key in ('total', 'limit'):
                self.ids[key].text = '{:.2f}'.format(val)
            elif key == 'expenses':
                continue
            else:
                self.ids[key].text = str(val)
        
    def on_press(self):
        details = self.details
        expenses = details['expenses']
        expenses.sort(reverse=True, key=lambda expense: str(expense['Date']))
        CategoryExpenses(self.details).open()


class CategorySetterButton(Button): # needed
    pass


class ExpenseItem(BoxLayout):

    def __init__(self, key, value, *args, **kwargs):     
        super(ExpenseItem, self).__init__(*args, **kwargs)
        self.key.text = key + ': '
        self.value.text = value


class Expense(ButtonBehavior, BoxLayout):

    def __init__(self, expense, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        self.expense = expense
        for key in EXPENSE_KEYS:
            if key in expense:
                self.add_widget(ExpenseItem(key, str(expense[key])))
        self.height = len(self.children) * 25
        
    def on_press(self, *args):
        # here we'll pop up a list to change the category
        popup = None
        expense = self.expense
        
        def set_category(button):
            app = App.get_running_app()
            category_cache = app.category_cache
            oid = expense['Order ID']
            current_category = expense['Category']
            current_category_expenses = category_cache[current_category]['expenses']
            target_expense = [exp for exp in current_category_expenses if exp['Order ID'] == oid][0]
            new_category = button.text
            target_expense['Category'] = new_category
            category_cache[current_category]['expenses'] = [exp for exp in current_category_expenses if exp['Order ID'] != oid]
            category_cache[new_category]['expenses'].append(target_expense)
            App.get_running_app().populate()
            popup.dismiss()
            self.parent.remove_widget(self)
            Clock.schedule_once(lambda x: CategoryExpenses.current.set_heading(), 0.5)
            
        dropdown = DropDown(size_hint=(1,1))
        for category in sorted(BUDGET.keys()):
            widget = CategorySetterButton(text=str(category), on_press=set_category)
            dropdown.add_widget(widget)
        popup = Popup(
            title=expense['Title'] if 'Title' in expense else expense['Description'],
            content=dropdown,
            size_hint=(.5,.9))
        popup.open()

               
class BViewApp(App):

    def __init__(self, *args, **kwargs):
        super(BViewApp, self).__init__(*args, **kwargs)
        self.save_button = self.expense_layout = self.operation_spinner = None
        Window.bind(on_request_close=self.exit_check)
        self.load_cache(self, *args)
        Clock.schedule_once(self.populate, 0.5)

    def load_cache(self, *args):
        # Load exceptions
        exceptions_cache = {}
        try:
            with open(EXCEPTIONS_CACHE_PATH) as f:
                exceptions_cache = json.load(f)
        except:
            print('Missing (or corrupt) exceptions cache, "{}", using empty file'.format(EXCEPTIONS_CACHE_PATH))
        # Load amazon cache
        amazon_cache = {}
        try:
            with open(AMAZON_CACHE_PATH) as f:
                amazon_cache = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(AMAZON_CACHE_PATH))
        # Apply amazon exceptions to amazon cache, add 'Date'
        for date, expenses in amazon_cache.items():
            for expense in expenses:
                category = expense['Category']
                if category in ['date-marker']:
                    continue
                id = expense.get('Order ID', None)
                if id in exceptions_cache:
                    expense['Category'] = exceptions_cache[id]
                elif category in AMAZON_CATEGORIES:
                    expense['Category'] = AMAZON_CATEGORIES[category]
                expense['Cost'] = expense.pop('Item Total')
                expense['Date'] = date
                expense['Source'] = 'Amazon'
                # trim to required keys
                expense = {key:val for key,val in expense.items() if key in AMAZON_EXPENSE_KEYS}
        dates = list(amazon_cache.keys())
        for date in dates: # convert all keys to datetime.date objects
            amazon_cache[datetime.datetime.strptime(date, DATE_FORMAT).date()] = amazon_cache.pop(date)
        # Load emoney cache
        emoney_cache = {}
        try:
            with open(EMONEY_CACHE_PATH) as f:
                emoney_cache = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(EMONEY_CACHE_PATH))
        dates = list(emoney_cache.keys())
        for date in dates: # convert all keys to datetime.date objects
             emoney_cache[datetime.datetime.strptime(date, DATE_FORMAT).date()] = emoney_cache.pop(date)
        # Apply exceptions to emoney cache, add 'Date'
        for date, expenses in emoney_cache.items():
            for expense in expenses:
                id = expense.get('Order ID', None)
                if id in exceptions_cache:
                    expense['Category'] = exceptions_cache[id]
                expense['Cost'] = expense.pop('Amount')
                expense['Date'] = date
                expense['Source'] = 'EMoney'
                # trim to required keys
                expense = {key:val for key,val in expense.items() if key in EMONEY_EXPENSE_KEYS}
                
        # Create the category cache by 'merging' amazon and emoney category cache's
        merged_cache = emoney_cache
        for date, expenses in merged_cache.items():
            if date in amazon_cache:
                expenses.extend(amazon_cache.pop(date))
        merged_cache.update(amazon_cache)
        # Create index by 'Category':
        period = 1
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        category_cache = {}
        for date, expenses in merged_cache.items():
            for expense in expenses:
                category = expense.get('Category', None)
                if category in ['Amazon', 'date-marker']:
                    continue
                if category == 'Kids' and 'Description' in expense and 'Derr' in expense['Description']:
                    expense['amount'] /= 2.0
                span = BUDGET[category]['span']
                details = category_cache.get(category, {'category': category, 'total':0, 'limit': BUDGET[category]['limit'], 'span':span,'expenses':[]})
                if date >= end_date - datetime.timedelta(days=span + period):
                    details['expenses'].append(expense)
                category_cache[category] = details
        self.category_cache = category_cache
        self.exceptions_cache = exceptions_cache

    def populate(self, *args):
        self.layout.data = []
        category_cache = self.category_cache
        categories = sorted(category_cache.keys()) 
        self.indexes = {val:key for key,val in dict(enumerate(categories)).items()}
        self.layout.data = [{'details': category_cache[category]} for category in categories]
        
    def exit_check(self, *args):
        if self.save_button.disabled:
           return False
        popup = Popup(title="App has unsaved changes. Really exit?", size_hint=(None, None), size=(220,140))
        layout = BoxLayout(orientation='horizontal', padding=(10,10,10,10), spacing=10)
        layout.add_widget(Button(text='Cancel', on_press=popup.dismiss))
        layout.add_widget(Button(text='Exit', on_press=self.stop))
        popup.add_widget(layout)
        popup.open()
        return True

    def set_range(self, months):
        from_date = (datetime.date.today() - datetime.timedelta(days=months * MONTH))
        self.from_date = datetime.datetime.strftime(from_date, DATE_FORMAT)
        self.load_cache()
        self.populate()

    def write_exceptions(self):
        # todo: prefer date/time based backups
        try:
            with open(EXCEPTIONS_CACHE_PATH + '.tmp','w+') as f:
                json.dump(self.exceptions_cache, f, indent=2)
            os.rename(EXCEPTIONS_CACHE_PATH + '.tmp', EXCEPTIONS_CACHE_PATH)
        except:
            popup = Popup(title='Failed to write exceptions to: {}'.format(EXCEPTIONS_CACHE_PATH))
            popup.add_widget(Button(text='OK'))
            popup.open()
        self.save_button.disabled = True


BViewApp().run()
