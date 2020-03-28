#!/usr/bin/env python3
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import BooleanProperty
from kivy.clock import Clock
import json
import pdb

from budget_defs import *

EXPENSE_KEYS = ['Order ID', 'Title', 'Category', 'Item Total','Shipping Address City','Buyer Name']

class ExpenseLabel(Label):
    pass

class DateLabel(Label):
    pass

class CategoryButton(Button):
    pass

class ExpenseItem(BoxLayout):

    def __init__(self, key, value, *args, **kwargs):     
        super(ExpenseItem, self).__init__(*args, **kwargs)
        self.key.text = key + ': '
        self.value.text = value
        

class Expense(ButtonBehavior, BoxLayout):

    known_category = BooleanProperty('False')

    def __init__(self, date, expense, known_category, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        self.height = len(EXPENSE_KEYS) * 25
        self.expense = expense
        self.category_label = None
        self.known_category = known_category


        for key,value in expense.items():
           if key in EXPENSE_KEYS:
               item = ExpenseItem(key, str(value))
               if key == 'Category':
                   self.category_label = item.ids['value']
               self.add_widget(item)

    def on_press(self, *args):
        # here we'll pop up a list to change the category
        dropdown = DropDown(size_hint=(1,1))
        popup = None
        
        def set_category(button):
            self.expense['Category'] = button.text
            self.category_label.text = button.text
            self.known_category = True
            popup.dismiss()

        for category in BUDGET.keys():
            widget = CategoryButton(text=str(category), on_press=set_category)
            dropdown.add_widget(widget)
        popup = Popup(
            title=self.expense['Title'],
            content=dropdown,
            size_hint=(.5,.5))
        popup.open()

               
class BrowserApp(App):

    def __init__(self, *args, **kwargs):
        super(BrowserApp, self).__init__(*args, **kwargs)
        try:
            with open(AMAZON_EXCEPTIONS_PATH) as f:
                self.amazon_exceptions = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON EXCEPTIONS, "{}", using empty file'.format(AMAZON_EXCEPTIONS_PATH))
            self.amazon_exceptions = {}
        try:
            with open(AMAZON_CACHE_PATH) as f:
                self.amazon_cache = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(AMAZON_CACHE_PATH))
            self.amazon_cache = {}
        try:
            with open(AMAZON_EXCEPTIONS_PATH) as f:
                self.amazon_exceptions = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON EXCEPTIONS, "{}", using empty file'.format(AMAZON_EXCEPTIONS_PATH))
            self.amazon_exceptions = {}

    def write_amazon_exceptions(self, *args):
        # todo: prefer date/time based backups
        if os.path.exists(AMAZON_EXCEPTIONS_PATH + '.prev'):
            os.rename(AMAZON_EXCEPTIONS_PATH + '.prev', AMAZON_CACHE_PATH + '.prev1')
        if os.path.exists(AMAZON_EXCEPTIONS_PATH):
            os.rename(AMAZON_EXCEPTIONS_PATH, AMAZON_CACHE_PATH + '.prev')
        try:
            with open(AMAZON_EXCEPTIONS_PATH,'w+') as f:
                json.dump(self.amazon_exceptions, f)
        except:
            print('Failed to write AMAZON EXCEPTIONS, "{}"'.format(AMAZON_EXCEPTIONS_PATH))

    def populate(self, expense_layout):

        def load(delta):
            dates = list(self.amazon_cache.keys())
            dates.sort(reverse=True)
            for date in dates:
                expenses = self.amazon_cache[date]
                if len(expenses) == 0:
                    continue
                expense_layout.add_widget(DateLabel(text=date))
                for expense in expenses:
                    category = expense['Category']
                    id = expense['Order ID']
                    if id in self.amazon_exceptions:
                        category = expense['Category'] = self.amazon_exceptions.get(id)
                    elif category in AMAZON_CATEGORIES:
                        category = expense['Category'] = AMAZON_CATEGORIES[category]
                    expense_layout.add_widget(Expense(date, expense, category in BUDGET))
            expense_layout.add_widget(Label())
            expense_layout.parent.scroll_to(expense_layout.children[-1])

        Clock.schedule_once(load, .1)


BrowserApp().run()