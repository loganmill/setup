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
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import BooleanProperty
from kivy.clock import Clock
import copy
import json
import pdb

from budget_defs import *

AMAZON_EXPENSE_KEYS = ['Title', 'Category', 'Item Total','Shipping Address City','Buyer Name', 'Order ID', 'Date']
EMONEY_EXPENSE_KEYS = ['Date','Description', 'Account', 'Category', 'Amount', 'Order ID', 'Date']


class BudgetLayout(BoxLayout):
    pass

class CategorySetterButton(Button):
    pass

class CategorySelectorButton(ToggleButton):
    pass


class CategoryLayout(BoxLayout):
    pass

class DateLabel(Label):
    pass

class ExpenseLabel(Label):
    pass

class ExpenseLayout(ScrollView):
    pass


class ExpenseItem(BoxLayout):

    def __init__(self, key, value, *args, **kwargs):     
        super(ExpenseItem, self).__init__(*args, **kwargs)
        self.key.text = key + ': '
        self.value.text = value
        

class Expense(ButtonBehavior, BoxLayout):

    known_category = BooleanProperty('False')

    def __init__(self, expense_keys, exceptions, expense, is_known_category, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        self.app = App.get_running_app()
        self.height = len(expense_keys) * 25
        self.exceptions = exceptions
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
            new_category = button.text
            current_category = self.category_label.text
            oid = expense['Order ID']
            # Move expense to new category in category structure. Note:
            # the expense iself.app.category_expenses is not the same object
            # as self.expense.
            category_expenses = self.app.category_expenses[current_category]
            target_expense = [exp for exp in category_expenses if exp['Order ID'] == oid][0]
            self.app.category_expenses[current_category] = \
                    [exp for exp in category_expenses if exp['Order ID'] != oid]
            target_expense['Category'] = new_category
            self.app.category_expenses[new_category].append(target_expense)
            # Set new category in expense and exceptions structure
            self.exceptions[oid] = self.category_label.text = expense['Category'] = new_category
            self.is_known_category = True
            self.app.save_button.disabled = False
            popup.dismiss()
        
        for category in sorted(BUDGET.keys()):
            widget = CategorySetterButton(text=str(category), on_press=set_category)
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
        from_date = (datetime.date.today() - datetime.timedelta(days=MONTH))
        self.from_date = datetime.datetime.strftime(from_date, DATE_FORMAT)
        Window.bind(on_request_close=self.exit_check)
        self.load_cache()
        Clock.schedule_once(self.populate, 0.1)

    def load_cache(self):
        from_date = self.from_date
        # Load amazon exceptions
        amazon_exceptions = {}
        try:
            with open(AMAZON_EXCEPTIONS_PATH) as f:
                amazon_exceptions = json.load(f)
        except:
            print('Missing (or corrupt) AMAZON EXCEPTIONS, "{}", using empty file'.format(AMAZON_EXCEPTIONS_PATH))
        # Load amazon cache
        amazon_cache = amazon_cache = {}
        try:
            with open(AMAZON_CACHE_PATH) as f:
                amazon_cache = json.load(f)
            amazon_cache = {key:val for key,val in amazon_cache.items() if key >= from_date }
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(AMAZON_CACHE_PATH))
        # Apply amazon exceptions to amazon cache, andd 'Date'
        for date, expenses in amazon_cache.items():
            for expense in expenses:
                category = expense['Category']
                if category in ['date-marker']:
                    continue
                id = expense.get('Order ID', None)
                if id in amazon_exceptions:
                    expense['Category'] = amazon_exceptions.get(id)
                elif category in AMAZON_CATEGORIES:
                    expense['Category'] = AMAZON_CATEGORIES[category]
                expense['Date'] = date
        # Load emoney exceptions
        emoney_exceptions = {}
        try:
            with open(EMONEY_EXCEPTIONS_PATH) as f:
                emoney_exceptions = json.load(f)
        except:
            print('Missing (or corrupt) EMONEY EXCEPTIONS, "{}", using empty file'.format(EMONEY_EXCEPTIONS_PATH))
        # Load emoney expenses
        emoney_cache = {}
        try:
            with open(EMONEY_CACHE_PATH) as f:
                emoney_cache = json.load(f)
            emoney_cache = {key:val for key,val in emoney_cache.items() if key > from_date}
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(EMONEY_CACHE_PATH))
        # Apply exceptions to emoney cache, add 'Date'

        for date, expenses in emoney_cache.items():
            for expense in expenses:
                id = expense.get('Order ID', None)
                if id in emoney_exceptions:
                    expense['Category'] = emoney_exceptions.get(id)
                expense['Date'] = date
        # Create the category cache by 'merging' amazon and emoney category cache's
        amazon_category_cache = copy.deepcopy(amazon_cache)
        emoney_category_cache = copy.deepcopy(emoney_cache)
        for date, expenses in emoney_category_cache.items():
            if date in amazon_category_cache:
                expenses.extend(amazon_category_cache.pop(date))
        emoney_category_cache.update(amazon_category_cache)
        # Now re-index by 'Category':
        category_expenses = {}
        for date, expenses in emoney_category_cache.items():
            for expense in expenses:
                category = expense.get('Category', None)
                expense_list = category_expenses.get(category, [])
                expense_list.append(expense)
                category_expenses[category] = expense_list
        self.amazon_cache = amazon_cache
        self.amazon_exceptions = amazon_exceptions
        self.emoney_cache = emoney_cache
        self.emoney_exceptions = emoney_exceptions
        self.category_expenses = category_expenses

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
                                  

    def populate(self, *args):
        self.layout.clear_widgets()
        operation = self.operation_spinner.text
        if operation == 'Amazon':
            self.populate_expenses(AMAZON_CATEGORIES, AMAZON_EXPENSE_KEYS, self.amazon_exceptions, self.amazon_cache)
        elif operation == 'Emoney':            
            self.populate_expenses({}, EMONEY_EXPENSE_KEYS, self.emoney_exceptions, self.emoney_cache)
        elif operation == 'Categories':
            self.populate_categories()
        elif operation == 'Budget':
            self.populate_budget()

    def populate_budget(self):
        layout = BudgetLayout()
        self.layout.add_widget(layout)

    def populate_categories(self):
        category_layout = CategoryLayout()
        categories_list = category_layout.ids['categories']
        expenses_list = category_layout.ids['expenses']
        details_label = category_layout.ids['details']

        def populate_category(button):
            expenses = App.get_running_app().category_expenses.get(button.text, [])
            expenses_list.clear_widgets()
            expenses.sort(reverse=True, key=lambda x: x['Date'])
            total = 0
            for expense in expenses:
                category = expense['Category']
                if category in ['date-marker', 'Amazon']:
                    continue
                is_amazon = 'Item Total' in expense  # Emoney has 'Amount'
                expenses_list.add_widget(
                    Expense(AMAZON_EXPENSE_KEYS if is_amazon else EMONEY_EXPENSE_KEYS,
                            self.amazon_exceptions if is_amazon else self.emoney_exceptions,
                            expense, True))
                total += expense['Item Total'] if 'Item Total' in expense else expense['Amount']
            expenses_list.height = sum([child.height + 20 for child in expenses_list.children])
            details_label.text = '{}: {:.2f}'.format(category, total)

        for category in BUDGET.keys():
            categories_list.add_widget(CategorySelectorButton(group='Categories', text=category,
               size_hint_y=None,
                   height=30,
                   on_press=populate_category))
        categories_list.height = len(categories_list.children) * 30
        self.layout.add_widget(category_layout)

    def populate_expenses(self, categories, keys, exceptions, cache):
        wait_popup = Popup(title='Loading data from {} to today'.format(self.from_date),
                   content=Label(text='Please wait...'), size_hint=(None, None), size=(400, 200))
        wait_popup.open()

        def _populate_expenses(delta):
            dates = list(cache.keys())
            dates.sort(reverse=True)
            expense_layout = ExpenseLayout()
            expense_list = expense_layout.ids['expense_list']
            for date in dates:
                expenses = cache[date]
                if len(expenses) == 0:
                    continue
                expense_list.add_widget(DateLabel(text=date))
                for expense in expenses:
                    category = expense['Category']
                    if category in ['date-marker', 'Amazon']:
                        continue
                    expense_list.add_widget(Expense(keys, exceptions, expense, category in BUDGET))
            expense_list.parent.scroll_to(expense_list.children[-1])
            self.layout.add_widget(expense_layout)
            wait_popup.dismiss()

        Clock.schedule_once(_populate_expenses)
        
    def scroll_to_unknown_expense(self, *args):
        # scroll to first unknown category
        if self.expense_layout:
            for child in reversed(self.expense_layout.children):
                if isinstance(child, Expense) and not(child.is_known_category):
                    self.expense_layout.parent.scroll_to(child)
                    break

    def write_exceptions(self):
        # todo: prefer date/time based backups
        for cache_path, exceptions in ((AMAZON_EXCEPTIONS_PATH, self.amazon_exceptions), (EMONEY_EXCEPTIONS_PATH, self.emoney_exceptions)):
            try:
                with open(cache_path + '.tmp','w+') as f:
                    json.dump(exceptions, f, indent=2)
                os.rename(cache_path + '.tmp', cache_path)
            except:
                popup = Popup(title='Failed to write exceptions to: {}'.format(cache_path))
                popup.add_widget(Button(text='OK'))
                popup.open()
        self.save_button.disabled = True


BrowserApp().run()
