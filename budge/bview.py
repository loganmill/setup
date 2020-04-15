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

AMAZON_EXPENSE_KEYS = ['Date', 'Title', 'Category', 'Item Total','Shipping Address City','Buyer Name', 'Order ID']
EMONEY_EXPENSE_KEYS = ['Date','Description', 'Account', 'Category', 'Amount', 'Order ID']

class CategoryExpenses(ModalView):
    pass

class ExpenseRow(ButtonBehavior,BoxLayout):

    details = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super(ExpenseRow, self).__init__(*args, **kwargs)

    def on_details(self, row, details):
        self.over_budget = self.details['total'] > self.details['limit']
        for key,val in self.details.items():
            if key in ('total', 'limit'):
                self.ids[key].text = '{:.2f}'.format(val)
            elif key in ('expenses', 'index'):
                pass
            else:
                self.ids[key].text = str(val)
        
    def on_press(self):
        app = App.get_running_app()
        details = self.details
        expenses = details['expenses']
        expenses.sort(reverse=True, key=lambda expense: str(expense['Date']))
        popup = CategoryExpenses()
        expense_list = popup.ids['expense_list']
        popup.ids['heading'].text = '{}: {:.2f}/{:.2f} {} days'.format(details['category'], details['total'], details['limit'], details['span'])
        for expense in expenses:
            is_amazon = 'Item Total' in expense  # Emoney has 'Amount'
            expense_list.add_widget(Expense(details, expense))
        popup.open()

class ExpenseRowLabel(Label):
    pass

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

    def __init__(self, details, expense, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        app = App.get_running_app()
        self.details = details
        self.expense = expense
        amazon_expense = 'Item Total' in expense  # Emoney has 'Amount'
        self.exceptions = app.amazon_exceptions if amazon_expense else app.emoney_exceptions
        expense_keys = AMAZON_EXPENSE_KEYS if amazon_expense else EMONEY_EXPENSE_KEYS
        self.height = len(expense_keys) * 25
        for key in expense_keys:
            self.add_widget(ExpenseItem(key, str(expense[key])))

    def on_press(self, *args):
        # here we'll pop up a list to change the category
        dropdown = DropDown(size_hint=(1,1))
        popup = None
        expense = self.expense
        
        def set_category(button):
            app = App.get_running_app()
            new_category = button.text
            current_category = self.category_label.text
            oid = expense['Order ID']
            category_expenses = app.category_data[current_category]['expenses']
            target_expense = [exp for exp in category_expenses if exp['Order ID'] == oid][0]
            app.category_data[current_category]['expenses'] = \
                [exp for exp in category_expenses if exp['Order ID'] != oid]
            target_expense['Category'] = new_category
            difference = target_expense['Item Total' if 'Item Total' in target_expense else 'Amount']
            app.category_data[new_category]['expenses'].append(target_expense)
            app.category_data[category]['total'] -= difference
            app.category_data[new_category]['total'] += difference
            # Set new category in expense and exceptions structure
            self.exceptions[oid] = self.category_label.text = expense['Category'] = new_category
            app.save_button.disabled = False
            popup.dismiss()
        
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
        self.load_cache()
        Clock.schedule_once(self.populate, 0.5)

    def load_cache(self):
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
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(AMAZON_CACHE_PATH))
        # Apply amazon exceptions to amazon cache, add 'Date'
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
        dates = list(amazon_cache.keys())
        for date in dates: # convert all keys to datetime.date objects
            amazon_cache[datetime.datetime.strptime(date, DATE_FORMAT).date()] = amazon_cache.pop(date)

        # Load emoney exceptions
        emoney_exceptions = {}
        try:
            with open(EMONEY_EXCEPTIONS_PATH) as f:
                emoney_exceptions = json.load(f)
        except:
            print('Missing (or corrupt) EMONEY EXCEPTIONS, "{}", using empty file'.format(EMONEY_EXCEPTIONS_PATH))
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
                if id in emoney_exceptions:
                    expense['Category'] = emoney_exceptions.get(id)
                expense['Date'] = date
                
        # Create the category cache by 'merging' amazon and emoney category cache's
        amazon_category_cache = copy.deepcopy(amazon_cache)
        merged_cache = copy.deepcopy(emoney_cache)
        for date, expenses in merged_cache.items():
            if date in amazon_category_cache:
                expenses.extend(amazon_category_cache.pop(date))
        merged_cache.update(amazon_category_cache)
        # Now re-index by 'Category':
        period = 1
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        category_data = {}
        for date, expenses in merged_cache.items():
            for expense in expenses:
                category = expense.get('Category', None)
                if category in ['Amazon', 'date-marker']:
                    continue
                if category == 'Kids' and 'Description' in expense and 'Derr' in expense['Description']:
                    expense['amount'] /= 2.0
                span = BUDGET[category]['span']
                details = category_data.get(category, {'category': category, 'total':0, 'limit': BUDGET[category]['limit'], 'span':span,'expenses':[]})
                if date >= end_date - datetime.timedelta(days=span + period):
                    details['total'] += expense['Item Total'] if 'Item Total' in expense else expense['Amount']
                    details['expenses'].append(expense)
                category_data[category] = details
        self.amazon_cache = amazon_cache
        self.amazon_exceptions = amazon_exceptions
        self.emoney_cache = emoney_cache
        self.emoney_exceptions = emoney_exceptions
        self.category_data = category_data
        #import pprint
        #print(pprint.pformat(self.category_data, indent=2))
        
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
        rows = []
        index = 0
        for category in sorted(self.category_data.keys()):
            details = self.category_data[category]
            details['index'] = index
            rows.append({'details': details})
            index += 1
        self.layout.data = rows

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


BViewApp().run()
