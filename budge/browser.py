#!/usr/bin/env python3
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
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

AMAZON_EXPENSE_KEYS = ['Order ID', 'Title', 'Category', 'Item Total','Shipping Address City','Buyer Name']
EMONEY_EXPENSE_KEYS = ['Order ID', 'Description', 'Account', 'Category', 'Amount']

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

    def __init__(self, date, expense_keys, expense, is_known_category, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        self.height = len(expense_keys) * 25
        self.expense = expense
        self.category_label = None
        self.is_known_category = is_known_category
        for key,value in expense.items():
           if key in expense_keys:
               item = ExpenseItem(key, str(value))
               if key == 'Category':
                   self.category_label = item.ids['value']
               self.add_widget(item)

    def on_press(self, *args):
        # here we'll pop up a list to change the category
        dropdown = DropDown(size_hint=(1,1))
        popup = None
        expense = self.expense
        
        def set_category(button):
            app = App.get_running_app()
            app.amazon_exceptions[expense['Order ID']] = \
                self.category_label.text = \
                expense['Category'] = button.text
            self.category_label.text = button.text
            self.is_known_category = True
            app.save_button.disabled = False
            popup.dismiss()
        
        for category in sorted(BUDGET.keys()):
            widget = CategoryButton(text=str(category), on_press=set_category)
            dropdown.add_widget(widget)
        popup = Popup(
            title=expense['Title'] if 'Title' in expense else expense['Description'],
            content=dropdown,
            size_hint=(.5,.9))
        popup.open()

               
class BrowserApp(App):

    def __init__(self, *args, **kwargs):
        super(BrowserApp, self).__init__(*args, **kwargs)
        self.save_button = self.expense_layout = self.operation_spinner = None
        Window.bind(on_request_close=self.exit_check)
        # Load amazon expenses
        try:
            with open(AMAZON_EXCEPTIONS_PATH) as f:
                self.amazon_exceptions = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON EXCEPTIONS, "{}", using empty file'.format(AMAZON_EXCEPTIONS_PATH))
            self.amazon_exceptions = {}
        try:
            with open(AMAZON_CACHE_PATH) as f:
                self.amazon_cache = json.load(f)
            self.amazon_cache = {key:val for key,val in self.amazon_cache.items() if key > '2020-02-08' }
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(AMAZON_CACHE_PATH))
            self.amazon_cache = {}
        # Load emoney expenses
        try:
            with open(EMONEY_CACHE_PATH) as f:
                self.emoney_cache = json.load(f)
            self.emoney_cache = {key:val for key,val in self.emoney_cache.items() if key > '2020-02-08'}
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(EMONEY_CACHE_PATH))
            self.emoney_cache = {}
        # initially, populate amazon expenses:
        Clock.schedule_once(self.populate, 0.1)

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

    def populate(self, *args):
        self.expense_layout.clear_widgets()
        print('populate {} {}'.format(self.operation_spinner.text, self.expense_layout))
        operation = self.operation_spinner.text
        if operation == 'Amazon':
            self.populate_expenses(AMAZON_CATEGORIES, AMAZON_EXPENSE_KEYS, self.amazon_cache, self.amazon_exceptions)
        elif operation == 'Emoney':            
            self.populate_expenses({}, EMONEY_EXPENSE_KEYS, self.emoney_cache, {})
        elif operation == 'Categories':
            self.populate_categories({}, {})

    def populate_categories(self, amazon_cache, emoney_cache):
        expense_layout = self.expense_layout
        expense_layout.orientation = 'horizontal'
        categories_layout = BoxLayout(orientation='vertical', size_hint=(None,None),
                                      width=300, height=30 * len(BUDGET.keys()))

        def populate_category(button):
            print(button.text)

        for category in BUDGET.keys():
            categories_layout.add_widget(ToggleButton(group='Categories', text=category,
               size_hint_y=None,
                   height=30,
                   on_press=populate_category))
        expense_layout.add_widget(categories_layout)
        expense_layout.add_widget(Widget())        
        


    def populate_expenses(self, categories, keys, cache, exceptions): # AMAZON_CATEGORIES, self.amazon_cache, self.amazon_exceptions
        dates = list(cache.keys())
        dates.sort(reverse=True)
        expense_layout = self.expense_layout
        expense_layout.orientation = 'vertical'
        for date in dates:
            expenses = cache[date]
            if len(expenses) == 0:
                continue
            expense_layout.add_widget(DateLabel(text=date))
            for expense in expenses:
                category = expense['Category']
                if category in ['date-marker', 'Amazon']:
                    continue
                if exceptions:
                    id = expense.get('Order ID', None)
                    if id in exceptions:
                        category = expense['Category'] = exceptions.get(id)
                    elif category in AMAZON_CATEGORIES:
                        category = expense['Category'] = AMAZON_CATEGORIES[category]
                expense_layout.add_widget(Expense(date, keys, expense, category in BUDGET))
        print(len(expense_layout.children))
        expense_layout.parent.scroll_to(expense_layout.children[-1])
        
    def scroll_to_unknown_expense(self, *args):
        # scroll to first unknown category
        if self.expense_layout:
            for child in reversed(self.expense_layout.children):
                if isinstance(child, Expense) and not(child.is_known_category):
                    self.expense_layout.parent.scroll_to(child)
                    break

    def write_amazon_exceptions(self, *args):
        # todo: prefer date/time based backups
        if os.path.exists(AMAZON_EXCEPTIONS_PATH + '.prev'):
            os.rename(AMAZON_EXCEPTIONS_PATH + '.prev', AMAZON_CACHE_PATH + '.prev1')
        if os.path.exists(AMAZON_EXCEPTIONS_PATH):
            os.rename(AMAZON_EXCEPTIONS_PATH, AMAZON_CACHE_PATH + '.prev')
        try:
            with open(AMAZON_EXCEPTIONS_PATH,'w+') as f:
                json.dump(self.amazon_exceptions, f, indent=2)
            self.save_button.disabled = True
        except:
            print('Failed to write AMAZON EXCEPTIONS, "{}"'.format(AMAZON_EXCEPTIONS_PATH))



BrowserApp().run()
