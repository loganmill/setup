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
import copy
import json
import pdb

from budget_defs import *

AMAZON_EXPENSE_KEYS = ['Title', 'Category', 'Item Total','Shipping Address City','Buyer Name', 'Order ID']
EMONEY_EXPENSE_KEYS = ['Description', 'Account', 'Category', 'Amount', 'Order ID']


class GrayWidget(Widget):
    pass

class ExpenseLabel(Label):
    pass

class DateLabel(Label):
    pass

class CategorySetterButton(Button):
    pass

class CategorySelectorButton(ToggleButton):
    pass


class ExpenseItem(BoxLayout):

    def __init__(self, key, value, *args, **kwargs):     
        super(ExpenseItem, self).__init__(*args, **kwargs)
        self.key.text = key + ': '
        self.value.text = value
        

class Expense(ButtonBehavior, BoxLayout):

    known_category = BooleanProperty('False')

    def __init__(self, expense_keys, expense, is_known_category, *args, **kwargs):
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
        # Load amazon exceptions
        from_date = self.from_date
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
        # Apply amazon exceptions to amazon cache
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
        # Load emoney expenses
        emoney_cache = {}
        try:
            with open(EMONEY_CACHE_PATH) as f:
                emoney_cache = json.load(f)
            emoney_cache = {key:val for key,val in emoney_cache.items() if key > from_date}
        except:
            print('Missing (or corrupt) AMAZON CACHE, "{}", using empty file'.format(EMONEY_CACHE_PATH))
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
        self.emoney_cache = emoney_cache
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
        self.expense_layout.clear_widgets()
        operation = self.operation_spinner.text
        if operation == 'Amazon':
            self.populate_expenses(AMAZON_CATEGORIES, AMAZON_EXPENSE_KEYS, self.amazon_cache)
        elif operation == 'Emoney':            
            self.populate_expenses({}, EMONEY_EXPENSE_KEYS, self.emoney_cache)
        elif operation == 'Categories':
            self.populate_categories({}, {})

    def populate_categories(self, amazon_cache, emoney_cache):
        expense_layout = self.expense_layout
        expense_layout.orientation = 'horizontal'
        categories_layout = BoxLayout(orientation='vertical', size_hint=(None,1),
                                      width=300, height=30 * len(BUDGET.keys()))
        category_expenses_layout = BoxLayout(orientation='vertical', spacing=30)

        def populate_category(button):
            category_expenses_layout.clear_widgets()
            expenses = App.get_running_app().category_expenses.get(button.text, [])
            for expense in expenses:
                category = expense['Category']
                if category in ['date-marker', 'Amazon']:
                    continue
                category_expenses_layout.add_widget(
                    Expense(AMAZON_EXPENSE_KEYS if 'Item Total' in expense else EMONEY_EXPENSE_KEYS, expense, True))
            category_expenses_layout.add_widget(Widget())

        for category in BUDGET.keys():
            categories_layout.add_widget(CategorySelectorButton(group='Categories', text=category,
               size_hint_y=None,
                   height=30,
                   on_press=populate_category))
        categories_layout.add_widget(GrayWidget())
        expense_layout.add_widget(categories_layout)
        expense_layout.add_widget(category_expenses_layout)

    def populate_expenses(self, categories, keys, cache):
        wait_popup = Popup(title='Loading data from {} to today'.format(self.from_date),
                   content=Label(text='Please wait...'), size_hint=(None, None), size=(400, 200))
        wait_popup.open()

        def _populate_expenses(delta):
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
                    expense_layout.add_widget(Expense(keys, expense, category in BUDGET))
            expense_layout.parent.scroll_to(expense_layout.children[-1])
            wait_popup.dismiss()

        Clock.schedule_once(_populate_expenses)
        
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
