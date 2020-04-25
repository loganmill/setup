from kivy.app import App
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import *
from kivy.utils import platform
from kivy.clock import Clock
from kivy.metrics import dp, sp
from budget_defs import *
import copy
import json
import pdb
import requests
from re import sub
import time

ANDROID = True  # for desktop testing of android

LAN_ADDRESS = 'http://10.0.0.129:5000'
WAN_ADDRESS = 'http://loganmill.net:5000'

# Only the following keys will be extracted from corresponding cache:
AMAZON_EXPENSE_KEYS = ['Date', 'Cost', 'Title', 'Category', 'Shipping Address City','Buyer Name',  'Source', 'Order ID']
EMONEY_EXPENSE_KEYS = ['Date', 'Cost', 'Description', 'Account', 'Category', 'Source', 'Order ID']
# Following merges previous 2: used for ordering on-screen presentation
EXPENSE_KEYS = ['Date', 'Cost', 'Title', 'Description', 'Category', 'Account', 'Shipping Address City', 'Buyer Name', 'Source', 'Order ID']
NON_EXPENSES = ['Income', 'Interest Income', 'Credit Card Payment', 'Investment Savings']

def sc(*args):
    # convenience for scaling
    return [dp(arg) for arg in args] if len(args) > 1 else dp(args[0])

def texture_from_label(**kwargs):
    # This function creates Label, then returns its texture.
    # Provide it with the same arguments you would use for a kivy.uix.Label.
    # Design purpose is for putting text into canvas, for example:
    # canvas:
    #    Rectangle:
    #        size: 100, 100
    #        texture: texture_from_label(text='hello', color=(1,1,1))
    l = CoreLabel(**kwargs)
    l.refresh()
    return l.texture


class BLabel(Label):
     pass


class BButton(Button):
     pass
 
class BDButton(BButton):
     pass

class BDialog(ModalView):
    pass

class GraphPanel(ModalView):

    @classmethod
    def launch(*args):
        GraphPanel().open()
        
    def on_open(self, *args):
        surface = self.ids['surface']
        date = datetime.date.today() - datetime.timedelta(days=365)
        sums = []
        app = App.get_running_app()
        date_cache = app.date_cache
        totals = {}
        for x in range(365):
            totals[date] = sum([expense.get('Cost', 0) \
                  for expense in date_cache.get(date, {})
                      if expense['Category'] not in NON_EXPENSES])
            date += datetime.timedelta(days=1)
        max_expense = max(totals.values())
        min_expense = min(totals.values())
        if min_expense < 0:
            max_expense = max(max_expense, -min_expense)
        max_height = sp(400)
        baseline = sc(50)
        x = sc(50) 
        y = baseline
        surface.width = x + len(totals) * sc(8) + x + sc(100)
        self.ids['scroller'].scroll_x = 1
        with surface.canvas:
            Color(rgba=(.5,.5,.5,1))
            Rectangle(size=surface.size, pos=surface.pos)
            for date, total in totals.items():
                Color(rgba=(0,0,1,1))
                if total < 0:
                    total = -total
                    Color(rgba=(0,1,0,1))
                Line(points=[x, y, x, y+int(max_height * (total/max_expense))], width=sc(2))
                if date.day == 1:
                    Color(rgba=(0,0,0,1))
                    Rectangle(size=sc(25,25),
                              pos=(x, y - sc(30)),
                              texture=texture_from_label(text=date.strftime('%b %y')))
                x += sc(8)
            # max daily budget line
            Color(rgba=(1,0,0,1))
            Line(points=[sc(50), max_height + baseline, x, max_height + baseline], width=sc(1))
            Color(rgba=(0,0,0,1))
            Rectangle(size=sc(100,24),
                pos=(x, max_height-sc(12) + sc(50)),
                texture=texture_from_label(text='${:.2f}'.format(max_expense)))
            # budgeted daily budget line
            budget_goal = sum([item['limit'] / item['span'] for item in BUDGET.values()])
            budget_height = int(max_height * (budget_goal/max_expense)) + baseline
            Color(rgba=(0,1,0,1))
            Line(points=[sc(50), budget_height, x, budget_height], width=sc(1))
            Color(rgba=(0,0,0,1))
            Rectangle(size=sc(100,24),
                pos=(x, budget_height-sc(12)),
                texture=texture_from_label(text='${:.2f}'.format(budget_goal)))


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
         self.ids['bar'].title.text = '{}: ${:.2f} available, ${:.2f}/${:.2f} spent, {} days'.format(
             details['category'], details['available'], details['total'], details['limit'], details['span'])

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
        self.details['total'] = total = sum([expense['Cost'] for expense in details['expenses']])
        limit = self.details['limit']
        self.details['available'] = max(limit-total, 0)
        self.over_budget = total > limit
        for key,val in self.details.items():
            if key in ('available', 'total', 'limit'):
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


class CategoryChooserRow(ButtonBehavior, Label):
    pass


class CategoryChooser(ModalView):
    pass

class ExpenseField(BoxLayout):

    def __init__(self, key, value, *args, **kwargs):     
        super(ExpenseField, self).__init__(*args, **kwargs)
        self.key.text = key + ': '
        self.value.text = value

class Expense(ButtonBehavior, BoxLayout):

    def __init__(self, expense, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        self.expense = expense
        for key in EXPENSE_KEYS:
            if key in expense:
                self.add_widget(ExpenseField(key, str(expense[key])))
        self.height = len(self.children) * sc(25)
        
    def on_press(self, *args):
        # here we'll pop up a list to change the category
        chooser = None
        expense = self.expense
        
        def set_category(new_category):
            app = App.get_running_app()
            category_cache = app.category_cache
            oid = expense['Order ID']
            current_category = expense['Category']
            current_category_expenses = category_cache[current_category]['expenses']
            target_expense = [exp for exp in current_category_expenses if exp['Order ID'] == oid][0]
            target_expense['Category'] = new_category
            category_cache[current_category]['expenses'] = [exp for exp in current_category_expenses if exp['Order ID'] != oid]
            category_cache[new_category]['expenses'].append(target_expense)
            app.dirty = True
            app.populate()
            chooser.dismiss()
            self.parent.remove_widget(self)
            Clock.schedule_once(lambda x: CategoryExpenses.current.set_heading(), 0.5)
            

        def confirm_set_category(button):
            new_category = button.text
            if button.text == expense['Category']:
                return # existing category chosen
            dialog = BDialog()
            dialog.message = """
                 [size=28sp]Confirm![/size]
 
 
  
                 Change category of:
  
                 [color=#b61f25]{}[/color]
  
                from:
  
                [color=#b61f25]{}[/color]
  
                to:
  
                [color=#b61f25]{}[/color]
                """.format(
                    self.expense['Description' if 'Description' in self.expense else 'Title'],
                    self.expense['Category'],
                    new_category)
            dialog.buttons = [
                BDButton(text='Change Category', on_press=lambda *args:[dialog.dismiss(), set_category(new_category)]),
                BDButton(text='Cancel', on_press=dialog.dismiss)]
            dialog.open()            

        chooser = CategoryChooser()
        category_list = chooser.ids['category_list']
        for category in sorted(BUDGET.keys()):
            widget = CategoryChooserRow(text=str(category), on_press=confirm_set_category)
            category_list.add_widget(widget)
        chooser.ids['bar'].title.text = \
            expense['Title'] if 'Title' in expense else expense['Description']
        chooser.open()
               
class BudgieApp(App):

    dirty = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(BudgieApp, self).__init__(*args, **kwargs)
        Window.bind(on_request_close=self.confirm_exit)
        self.period = 1
        Clock.schedule_once(self.load_cache, 0)
        
    def get_cache(self, path):
        if platform == 'android' or ANDROID:
            err = ''
            for address in (LAN_ADDRESS, WAN_ADDRESS):
               full_path = { 'amazon': address + '/amazon',
                             'emoney': address + '/emoney',
                             'exceptions': address + '/exceptions'
                           }.get(path, None)
               if path:
                  try: 
                      response = requests.get(full_path, timeout=3.0)
                      return json.loads(response.text)
                  except Exception as ex:
                      err += '{}\n'.format(ex)
            raise Exception(err)
        else: # platform == linux, windows
            full_path = { 'amazon': AMAZON_CACHE_PATH,
                          'emoney': EMONEY_CACHE_PATH,
                          'exceptions': EXCEPTIONS_CACHE_PATH
                        }.get(path, None)
            with open(full_path) as f:
                return json.load(f)

    def load_cache(self, *args):
        while True:
            try:
                amazon_cache = self.get_cache('amazon')
                emoney_cache = self.get_cache('emoney')
                exceptions_cache = self.get_cache('exceptions')
                break
            except Exception as ex:
                dialog = BDialog()
                dialog.message = """
                [size=28sp]Error: Failed to budget data.[/size]
 
   
                [color=666666]{}[/color]
                """.format(ex)
                dialog.buttons = [BDButton(text='Retry', on_press=lambda *args:
                                 [Clock.schedule_once(dialog.dismiss), Clock.schedule_once(self.load_cache, 0.5)]),
                                  BDButton(text='Exit', on_press=sys.exit)]
                dialog.open()
                return
                
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
                elif category not in BUDGET:
                    expense['Category'] = 'Unknown Amazon'
                expense['Cost'] = expense.pop('Item Total')
                expense['Date'] = date
                expense['Source'] = 'Amazon'
                # trim to required keys
                expense = {key:val for key,val in expense.items() if key in AMAZON_EXPENSE_KEYS}
        dates = list(amazon_cache.keys())
        for date in dates: # convert all keys to datetime.date objects
            amazon_cache[datetime.datetime.strptime(date, DATE_FORMAT).date()] = amazon_cache.pop(date)
        dates = list(emoney_cache.keys())
        for date in dates: # convert all keys to datetime.date objects
             emoney_cache[datetime.datetime.strptime(date, DATE_FORMAT).date()] = emoney_cache.pop(date)
        # Apply exceptions to emoney cache, add 'Date'
        for date, expenses in emoney_cache.items():
            for expense in expenses:
                id = expense.get('Order ID', None)
                category = expense.get('Category', None)
                if category in ['date-marker']:
                    continue
                if id in exceptions_cache:
                    expense['Category'] = exceptions_cache[id]
                elif category not in BUDGET:
                    expense['Category'] = 'Unknown Emoney'
                expense['Cost'] = expense.pop('Amount')
                expense['Date'] = date
                expense['Source'] = 'EMoney'
                # trim to required keys
                expense = {key:val for key,val in expense.items() if key in EMONEY_EXPENSE_KEYS}
        # Create the category cache by 'merging' amazon and emoney category cache's
        merged_cache = amazon_cache
        for date, expenses in merged_cache.items():
            if date in emoney_cache:
                expenses.extend(emoney_cache.pop(date))
        merged_cache.update(emoney_cache)
        self.date_cache = merged_cache
        # Create index by 'Category':
        period = self.period
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        category_cache = {}
        self.max_date = max(merged_cache.keys())
        for date, expenses in merged_cache.items():
            for expense in expenses:
                id = expense.get('Order ID', None)
                category = expense.get('Category', None)
                if category in ['Amazon', 'date-marker']:
                    continue
                if id in exceptions_cache:
                    expense['Category'] = exceptions_cache[id]
                if category == 'Kids' and 'Description' in expense and 'Derr' in expense['Description']:
                    expense['amount'] /= 2.0
                try:
                    span = BUDGET[category]['span']
                except:
                    pdb.set_trace()
                details = category_cache.get(category,
                    {'category': category,
                     'available': 0,
                     'total':0,
                     'limit': BUDGET[category]['limit'],
                     'span':span,
                     'expenses':[]})
                if date >= end_date - datetime.timedelta(days=span + period):
                    details['expenses'].append(expense)
                category_cache[category] = details
        self.category_cache = category_cache
        self.exceptions_cache = exceptions_cache
        self.dirty = False
        self.populate()

    def populate(self, *args):
        self.layout.data = []
        category_cache = self.category_cache
        categories = sorted(category_cache.keys()) 
        self.indexes = {val:key for key,val in dict(enumerate(categories)).items()} # used to alternate colours
        self.layout.data = [{'details': category_cache[category]} for category in categories]
        self.root.ids['bar'].title.text = '{}'.format(
             (self.max_date + datetime.timedelta(days=self.period)).strftime('%a %b %d %Y'))

    def confirm_reload(self, *args):
        if self.dirty:
            dialog = BDialog()
            dialog.message = """
                [size=28sp]Confirm![/size]

                 
                Budgie has unsaved changes.
 
 
                [size=28sp][color=#b61f25]Really reload?[/color][/size]"""
            dialog.buttons = [BDButton(text='Cancel', on_press=dialog.dismiss),
                              BDButton(text='Reload', on_press=self.load_cache)]

            dialog.open()
            return True
        return False

    def confirm_exit(self, *args):
        if self.dirty:
            dialog = BDialog()
            dialog.message = """
                [size=28sp]Confirm![/size]

                 
                Budgie has unsaved changes.
 
 
                [size=28sp][color=#b61f25]Really exit?[/color][/size]"""
            dialog.buttons = [BDButton(text='Cancel', on_press=dialog.dismiss),
                              BDButton(text='Exit', on_press=sys.exit())]

            dialog.open()
            return True
        return False

    def menu(self,button):  # access to auxiliary operations
        dialog = BDialog(background_color=(0,0,0,0), size_hint=(None,None),
                         pos_hint={'top': 1.0, 'right': 1.0})
        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=sp(50), spacing=sp(10))
        button_box.add_widget(Widget())
        button_box.add_widget(BButton(size_hint=(None,None),size=sc(50,50),
               background_normal='reload.png', background_color=(0,0,0,1), on_press=self.confirm_reload))
        button_box.add_widget(BButton(size_hint=(None,None),size=sc(50,50),
               background_normal='close.png', background_color=(0,0,0,1), on_press=self.confirm_exit))
        dialog.widgets =  [button_box,
                           BDButton(text='Expense Graph', height=sc(50), on_press=lambda *args:
                               [Clock.schedule_once(dialog.dismiss),Clock.schedule_once(GraphPanel.launch)]),
                           BDButton(text='Expense Graph', height=sc(50), on_press=lambda *args:
                               [Clock.schedule_once(dialog.dismiss),Clock.schedule_once(GraphPanel.launch)]),
                           BDButton(text='Expense Graph', height=sc(50), on_press=lambda *args:
                               [Clock.schedule_once(dialog.dismiss),Clock.schedule_once(GraphPanel.launch)]),

                         ]
        content = dialog.children[0]
        dialog.width = sum([child.width for child in content.children]) 
        dialog.height = sum([child.height for child in content.children]) + content.spacing * len(content.children)
        dialog.open()
        dialog.message = ''
        return True


    def write_exceptions(self):
        error = ''
        if platform == 'android' or ANDROID:
            for address in (LAN_ADDRESS, WAN_ADDRESS):
                try:
                    requests.put('{}/put_exceptions'.format(address), data=json.dumps(self.exceptions_cache), timeout=2.0)
                    self.dirty = False
                    return
                except Exception as ex:
                    error += '{}\n'.format(ex)
        else:
            try:
                with open(EXCEPTIONS_CACHE_PATH + '.tmp','w+') as f:
                    json.dump(self.exceptions_cache, f, indent=2)
                os.rename(EXCEPTIONS_CACHE_PATH + '.tmp', EXCEPTIONS_CACHE_PATH)
                self.dirty = False
                return
            except Exceptions as ex:
                error = '{}'.format(ex)
        dialog = BDialog()
        dialog.message = """
           [size=28sp]Error: Failed to upload changes:
 
           [color=#666666]{}[/color]
           """.format(error)
        dialog.buttons = [BDButton(text='OK', on_press=dialog.dismiss),
                          BDButton(text='Exit', on_press=sys.exit)]
        dialog.open()


if __name__=='__main__':
    BudgieApp().run()
