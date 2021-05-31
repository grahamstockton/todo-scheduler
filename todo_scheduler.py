import os, time, json, operator, math
from itertools import product
OS_TYPE = os.name

# This is for the flash invalid
try:
    from termcolor import colored
    HAS_TERMCOLOR = True
except: HAS_TERMCOLOR = False

# This is for cropping the screen -- Thought about doing this with json, ini, or yaml, but we're gonna just do it here with scary globals. 
# I don't want to make people install things, and I don't want a whole file for what is right now one variable
def CONST_START_TIME(): return " 8:00a"
def CONST_END_TIME(): return "12:00a"
def CONST_ROW_NUMBER_THRESHOLD(): return 50

class BannerItem: # Not going to make getters and setters for everything here, just going to make sure we use good practices for this code
    def __init__(self,title="",start_time='-1',end_time='-1',description=""):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.priority = 0

    def reschedule(self,start_time,end_time):
        self.start_time = start_time
        self.end_time = end_time

    def redescribe(self,description):
        self.description = description
    
    def __str__(self):
        return "{}: {}".format(self.title,self.description)

class TodoItem:
    def __init__(self,title="",description="",done_or_not=False): # I thought about adding time here, but the point of a todo item is doneness. If necessary, it is completely ok to just put the time in the description
        self.title = title
        self.description = description
        self.done_or_not = done_or_not

    def mark_done(self):
        self.done_or_not = True

    def mark_undone(self):
        self.done_or_not = False

    def redescribe(self,description):
        self.description = description

    def __str__(self):
        if self.done_or_not:
            return "{} ({}): {}".format(self.title,"Done",self.description)
        else:
            return "{} ({}): {}".format(self.title,"Not Done",self.description)

class Screen: 
    times_list = ["{}:{}{}".format(i,j,k) for (k,i,j) in product(["a","p"],["12"," 1"," 2"," 3"," 4"," 5"," 6"," 7"," 8"," 9","10","11"],["00","15","30","45"])] + ["12:00a"]

    def __init__(self,banners=[],todos=[]):
        self.banners = banners
        self.todos = todos

    def addBanner(self,banner):
        self.banners.append(banner)

    def addTodo(self,todo):
        self.todos.append(todo)

    def deleteItem(self,index,object_type):
        if object_type == 'banner':
            if not (index < len(self.banners)): return
            self.banners = sorted(self.banners, key=operator.attrgetter('start_time'))
            del self.banners[index]
        elif object_type == 'todo':
            if not (index < len(self.todos)): return
            del self.todos[index]

    def drawScreen(self):
        self.banners = sorted(self.banners, key=operator.attrgetter('start_time')) # This sucks, but for whatever reason operator doesn't seem to work with sort(), only sorted()
        os.system('cls' if OS_TYPE == 'nt' else 'clear')
        _, lines = os.get_terminal_size()
        if lines < CONST_ROW_NUMBER_THRESHOLD():
            for item in self.banners: print(item)
            for item in self.todos: print(item)
        else: 
            self.prioritizeBanners()
            tab = self.getPrintTableau()

            if tab: # This is really messy and should be done better. Hopefully I'll have time to get back to it eventually.
                i = 0
                banner_index = -10
                todo_index = -3
                while (i < 97) and (self.times_list[i] != CONST_START_TIME()): i += 1
                while (i < 97):
                    if self.times_list[i] == CONST_END_TIME():
                        print(self.times_list[i] + tab[i])
                        break
                    elif banner_index < -1:
                        print(self.times_list[i] + tab[i])
                        banner_index += 1
                    elif banner_index == -1:
                        print("{}{}   Scheduled Events --------------------------".format(self.times_list[i],tab[i]))
                        banner_index += 1
                    elif banner_index < len(self.banners):
                        print("{}{}     ({}) -- {}".format(self.times_list[i],tab[i],str(banner_index),str(self.banners[banner_index])))
                        banner_index += 1
                    elif todo_index < -1:
                        print(self.times_list[i] + tab[i])
                        todo_index += 1
                    elif todo_index == -1:
                        print("{}{}   TODO List ---------------------------------".format(self.times_list[i],tab[i]))
                        todo_index += 1
                    elif todo_index < len(self.todos):
                        print("{}{}     ({}) -- {}".format(self.times_list[i],tab[i],str(todo_index),str(self.todos[todo_index])))
                        todo_index += 1
                    else:
                        print(self.times_list[i] + tab[i])
                    i += 1

    def promptUser(self,prompt):
        self.drawScreen()
        return input(prompt)

    def flashInvalid(self):
        if HAS_TERMCOLOR:
            snippet = colored(':','red')
        else:
            snippet = 'X:'
        self.drawScreen() # this will make sure to get rid of the existing text
        for i in range(2):
            print(snippet,end='\r')
            time.sleep(.3)
            print(':',end='\r')
            time.sleep(.3)

    def reschedule(self, index, start_time, end_time):
        sorted(self.banners, key=operator.attrgetter('start_time'))[index].reschedule(start_time,end_time)

    def redescribe(self, index, description, type_of_object):
        if type_of_object == 'banner':
            sorted(self.banners,key=operator.attrgetter('start_time'))[index].redescribe(description)
        elif type_of_object == 'todo':
            self.todos[index].redescribe(description)

    def markTodo(self, index, state='done'):
        if state == 'done':
            self.todos[index].mark_done()
        elif state == 'undone':
            self.todos[index].mark_undone()

    def writeToJSON(self,filename='schedule_objects.json'):
        with open(filename,'w') as file:
            items_list = []
            for obj in self.banners:
                items_list.append(encode_BannerItem(obj))
            for obj in self.todos:
                items_list.append(encode_TodoItem(obj))
            json.dump(items_list,file)
            file.close()

    def prioritizeBanners(self):
        if not self.banners: return
        if len(self.banners) == 1:
            self.banners[0].priority = 0
            return

        # Get the very first banner, give it priority 0
        self.banners = sorted(self.banners, key=operator.attrgetter('start_time'))
        self.banners[0].priority = 0

        # Get all banners that overlap with the first, we know that we can give them their own priority with no overlaps
        prio = 1
        current_banner_index = 1
        for banner in self.banners[1:]:
            if banner.start_time <= self.banners[0].end_time:
                banner.priority = prio
                prio += 1
                current_banner_index += 1
            else: break

        # From now on we'll have to check for overlaps -- This implementation just feels really bad, but it works. It is approximately n^2, but we shouldn't be working with that many banners so it's probably ok
        while current_banner_index < len(self.banners):
            self.banners[current_banner_index].priority = 0
            current_banner_index += 1
            for banner in self.banners[current_banner_index+1:]:
                candidate_prio = 0
                while True:
                    taken_prios = []
                    for previous_banner in self.banners[:current_banner_index]:
                        if previous_banner.end_time >= banner.start_time:
                            taken_prios.append(previous_banner.priority)
                    while candidate_prio in taken_prios:
                        candidate_prio += 1
                    banner.priority = candidate_prio
                    current_banner_index += 1

    def getPrintTableau(self):
        if not self.banners: return []
        self.banners = sorted(self.banners, key=operator.attrgetter('start_time'))
        columns = max([banner.priority for banner in self.banners]) + 1
        tableau = [["   "]*(columns) for i in range(97)]
        for index, banner in enumerate(self.banners):

            start_index = int(banner.start_time[:-2])*4 + int(banner.start_time[-2:])//15
            end_index = int(banner.end_time[:-2])*4 + math.ceil(int(banner.end_time[-2:])/15) # thought about making my own ceil function for this,bc I don't like importing math just for this line, but decided that wasn't worth it
            halfway_point = (start_index + end_index)//2
            
            # Here the actual drawing takes place
            tableau[start_index][banner.priority] = " ┬ "
            tableau[end_index][banner.priority] = " ┴ "
            for it in range(start_index+1,end_index):
                if it == halfway_point:
                    tableau[it][banner.priority] = "({})".format(index)
                else:
                    tableau[it][banner.priority] = " │ "

        # Join tableau
        tableau = ["".join(row) for row in tableau]
        return tableau



    def __str__(self):
        print("printing not supported currently for Screen class")

def encode_BannerItem(o):
    if isinstance(o,BannerItem):
        return {'title':o.title,'start_time':o.start_time,'end_time':o.end_time,'description':o.description,o.__class__.__name__:True}
    else:
        raise TypeError('Object of type BannerItem is not JSON serializable')

def encode_TodoItem(o):
    if isinstance(o,TodoItem):
        return {'title':o.title,'description':o.description,'done_or_not':o.done_or_not,o.__class__.__name__:True}
    else:
        raise TypeError('Object of type TodoItem is not JSON serializable')

def decode_BannerItem(dct):
    if BannerItem.__name__ in dct:
        return BannerItem(title=dct['title'],start_time=dct['start_time'],end_time=dct['end_time'],description=dct['description'])
    else: return dct

def decode_TodoItem(dct):
    if TodoItem.__name__ in dct:
        return TodoItem(title=dct['title'],description=dct['description'],done_or_not=dct['done_or_not'])
    else: return dct

def clear_for_new_day(screen,json_filename):
    file = open(json_filename,'w')
    file.close() # This clears the contents of the file
    return Screen()

def convert_to_24hr_time(raw_time): # note this takes in a str
    pm = (not 'a' in raw_time) # chose pm by default (I wake up late)
    numeric_time = ''.join([i for i in raw_time if i.isnumeric()])
    if pm:
        if (numeric_time[:2] == '12') and (len(numeric_time) == 4):
            return numeric_time
        else:
            return str(1200+int(numeric_time.ljust(3,'0')))
    else:
        if (numeric_time[:2] == '12') and (len(numeric_time) == 4):
            return str(-1200+int(numeric_time)).rjust(4,"0")
        else:
            return numeric_time.ljust(3,'0')

# Functions for actual operation of app
def get_Banners_list(filename="schedule_objects.json"):
    Banners_list = []
    with open(filename,'r') as file:
        try:
            list_of_objects = json.load(file)
            for obj in list_of_objects:
                if BannerItem.__name__ in obj:
                    Banners_list.append(decode_BannerItem(obj))
        except:
            return []
    file.close()
    return Banners_list

def get_Todos_list(filename='schedule_objects.json'):
    Todos_list = []
    with open(filename,'r') as file:
        try:
            list_of_objects = json.load(file)
            for obj in list_of_objects:
                if TodoItem.__name__ in obj:
                    Todos_list.append(decode_TodoItem(obj))
        except:
            return []
    file.close()
    return Todos_list


# Was going to put this into the screen class as a method, but realized that it is probably specific to this program and also is going to be pretty long. For these reasons I'm just going to make it a few functions outside of the class
def generate_Text_Display(banners,todos):
    pass

# Set up json data
json_filename = 'schedule_objects.json'
if os.path.isfile(json_filename):
    banners = get_Banners_list()
    todos = get_Todos_list()
else:
    os.system('type nul > {}'.format(json_filename) if OS_TYPE == 'nt' else 'touch {}'.format(json_filename))
    banners = []
    todos = []

# Make screen instance    
screen = Screen(banners[:],todos[:]) # Initially had this with the actual lists an not copies and everything worked and was probably more efficient, but it seemed like pretty bad practice
welcome_message = ""

# Main loop
while True:

    # Refresh after each command
    screen.drawScreen()
    command = input("{}:".format(welcome_message)).strip().lower() # This is the bottom line of the application, designed for user input
    
    # All of the commands available
    if command == ('q' or 'quit'):
        exit()

    # Newday will clear the json file and all of the objects
    elif command == ('n' or 'newday'):
        screen = clear_for_new_day(screen,json_filename)

    # Schedule will create a schedule object, put it in the JSON file, and update the display
    elif command in ('s', 'sch', 'schedule'):
        title = screen.promptUser('title:')
        start_time = screen.promptUser('start time (e.g. 730a or 8p):')
        end_time = screen.promptUser('end time (e.g. 730a or 8p):')
        description = screen.promptUser('description:')
        screen.addBanner(BannerItem(title,convert_to_24hr_time(start_time),convert_to_24hr_time(end_time),description)) # This passes our start and end times through our time converter. It gives back a military time int
        screen.writeToJSON(json_filename)

    # Reschedule will change the times on a schedule item
    elif command in ('r', 'resc', 'reschedule'):
        item_index = int(screen.promptUser('index: ')) - 1
        new_start_time = screen.promptUser('start time (e.g. 730a or 8p): ')
        new_end_time = screen.promptUser('end time (e.g. 730a or 8p): ')
        screen.reschedule(item_index,convert_to_24hr_time(new_start_time),convert_to_24hr_time(new_end_time))
        screen.writeToJSON(json_filename)

    # Edits an existing schedule item's description
    elif command in ('e', 'edit'):
        item_index = int(screen.promptUser('index: ')) - 1
        new_description = screen.promptUser('description: ')
        screen.redescribe(item_index,new_description,'banner')
        screen.writeToJSON(json_filename)

    # Deletes an existing schedule item
    elif command in ('d','del', 'delete'):
        item_index = int(screen.promptUser('index: ')) - 1
        screen.deleteItem(item_index,'banner')
        screen.writeToJSON(json_filename)

    # Creates a todo item
    elif command in ('t', 'todo'):
        title = screen.promptUser('title: ')
        description = screen.promptUser('description: ')
        screen.addTodo(TodoItem(title,description))
        screen.writeToJSON(json_filename)

    # Marks a todo item as done
    elif command == 'done':
        item_index = int(screen.promptUser('index: ')) - 1
        screen.markTodo(item_index,'done')
        screen.writeToJSON(json_filename)

    # Marks a todo item as undone
    elif command in ('u', 'undo', 'undone'):
        item_index = int(screen.promptUser('index: ')) - 1
        screen.markTodo(item_index,'undone')
        screen.writeToJSON(json_filename)

    # Deletes a todo item
    elif command in ('dt', 'delt', 'delete-todo'):
        item_index = int(screen.promptUser('index: ')) - 1
        screen.deleteItem(item_index,'todo')
        screen.writeToJSON(json_filename)

    # Edits the description of a todo item
    elif command in ('te', 'tedit', 'todo-edit'):
        item_index = int(screen.promptUser('index: ')) - 1
        new_description = screen.promptUser('description: ')
        screen.redescribe(item_index,new_description,'todo')
        screen.writeToJSON(json_filename)

    # Plays our beautiful flashing animation -- Only works if termcolor is installed. Otherwise does nothing.
    else:
        screen.flashInvalid()
