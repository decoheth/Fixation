# Import Libraries
import sys
import logging
import random


import circlify

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from mysql.connector import connect, Error

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import *



# Variables
# GUI parameters 
title = "Fixation"
app_title = "Fixation"
w = 800
h = w

# Prevent circlify module warning for unexpected key, by only displaying logs of level ERROR and above
logging.getLogger("circlify").setLevel(logging.ERROR)

# Define Functions

# Function to create new entry to topic table
def add_topic(name,category,size=1):



     

    query = "INSERT INTO topic (name, category,size) VALUES (%s,%s,%s)"
    values = (name, category, size)

    # Check if topic already exists
        # if so then alter table and increase the size
    
    print("Topic created:",name)
    # Connect to db
    mysql_connect(query,values)

# Function to create new entry to category table
def add_category(name,colour=""):

    # Error Checking
    if colour=="":
        colour = rand_colour()

    query = "INSERT INTO category (name, colour) VALUES (%s,%s)"
    values = (name, colour)

    print("Category created:",name)
    # Connect to db
    mysql_connect(query,values)

# Function to connect to mySQL database and execute query
def mysql_connect(q, v=''):
    # Connect to mySQL database
    try:
        with connect(
            host="localhost",
            user="admin",
            password="admin",
            database="fixations"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(q,v)
                connection.commit()

    # Raise error             
    except Error as e:
        print(e)

def fetch_topic():
    fetched = []

    try:
        with connect(
            host="localhost",
            user="admin",
            password="admin",
            database="fixations"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM topic")
                result = cursor.fetchall()
                for row in result:
                    fetched.append(row)
                return(fetched)
                
            
    # Raise error             
    except Error as e:
        print(e)


def fetch_category():
    fetched = []

    try:
        with connect(
            host="localhost",
            user="admin",
            password="admin",
            database="fixations"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM category")
                result = cursor.fetchall()
                for row in result:
                    fetched.append(row)
                #print(fetched)
                return(fetched)
            
    # Raise error             
    except Error as e:
        print(e)

def sync_tables():
    # Check that topic's category is real, if not then create new category entry

    # fetch topic, assign color and category_id from category table
    cat_fetched = fetch_category()
    top_fetched = fetch_topic()

    for i in range(len(cat_fetched)):
        for k in range(len(top_fetched)):
            # If topic's category name = category name
            if top_fetched[k][2] == cat_fetched[i][1]:
                mysql_connect("UPDATE topic SET category_id={a} WHERE id={b}".format(a=cat_fetched[i][0], b=top_fetched[k][0]))
                mysql_connect("UPDATE topic SET colour='{a}' WHERE id={b}".format(a=cat_fetched[i][2], b=top_fetched[k][0]))

def rand_colour():
    r = lambda: random.randint(0,255)
    colour = '#{:02x}{:02x}{:02x}'.format(r(), r(), r())
    return(colour)
    
# Compiles topic table to be plotted
def topic_data():



    # Get max category_id
    catid_max = 1
    try:
        with connect(
            host="localhost",
            user="admin",
            password="admin",
            database="fixations"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(category_id) FROM topic")
                result = cursor.fetchall() 
                for row in result:
                    catid_max = (row[0])
    # Raise error             
    except Error as e:
        print(e)


    # Initiate hierarchal dataset
    master_list = {'id': title, 'datum': 1, 'children' : [] }
    middle_list = {}
    sub_list = {} 
     
    sub_array = []
    outer_array = []
    master_array = []

    # Itterate for each category
    for i in range(catid_max):
        sum = 0

        try:
            with connect(
                host="localhost",
                user="admin",
                password="admin",
                database="fixations"
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM topic WHERE category_id = {}".format(i+1))
                    result = cursor.fetchall()  
                                     
                    for row in result:  
                        # Get id and datum values                                         
                        sub_list["id"] = row[1]
                        sub_list["datum"] = row[5]
                        # Add datum size to sum
                        sum += row[5]
                        sub_list["colour"] = row[4]
                        # Append list to array
                        sub_array.append(sub_list)
                        # Empty list
                        sub_list = {}
                    
                        
                    # Set middle list (category)     
                    middle_list["id"] = row[2]
                    middle_list["datum"] = sum
                    middle_list["colour"] = row[4]

                    # Insert sub array as children of middle list
                    middle_list["children"] = sub_array 

        # Raise connection error             
        except Error as e:
            print(e)


        # Append middle list (category) to outer array
        outer_array.append(middle_list)

        # Empty arrays
        sub_array = []
        sub_list = {}
        middle_list = {}


    # Outside of for loop    

    # Insert the outer array as the children of master list
    master_list["children"] = outer_array
    # Convert to array
    master_array.append(master_list)
    # Return the master array
    return(master_array)


def create_test_batch():
    add_category('Military','#025c18')
    add_category('Physics','#3684a8')
    add_category('Art','#c4c421')
    add_category('Technology','#2343b8')
    add_category('Books','#10c790')

    add_topic('US Navy','Military',34)
    add_topic('AI Art','Art',3)
    add_topic('US Air Force','Military',12)
    add_topic('Quantum Physics','Physics',5)
    add_topic('Irish Navy','Military',8)
    add_topic('Python GUI','Technology',4)
    add_topic('Brandon Sanderson','Books',12)
    add_topic('Smart Homes','Technology',3)
    add_topic('Submarines','Military',5)
    

def dump_all():
    mysql_connect("DROP TABLE topic")
    mysql_connect("DROP TABLE category")

    print("All tables have been deleted.")

def rebuild():
    dump_all()
    mysql_connect(
        """CREATE TABLE category (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            name VARCHAR(255), 
            colour VARCHAR(255))"""
            )
    
    mysql_connect(
        """CREATE TABLE topic (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            name VARCHAR(255), 
            category VARCHAR(255), 
            category_id INT,  
            colour VARCHAR(255), 
            size INT)"""
            )


    create_test_batch()
    sync_tables()

    print("Database rebuilt and populated")





# Classes

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

# Create GUI

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle(app_title)
        self.resize(w,h)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)



        # Tab 1
        layout1_1 = QVBoxLayout()
        layout1_2 = QHBoxLayout()
        layout1_3 = QHBoxLayout()

        layout1_1.setContentsMargins(0,0,0,0)
        layout1_1.setSpacing(5)

        # First Row

        # Button connected to 'plot' method to replot figure
        replot_btn = QPushButton(QIcon("static/icons/refresh.png"), "Refresh Plot", self)
        replot_btn.setIconSize(QSize(16,16))
        replot_btn.clicked.connect(self.plot)

        
        layout1_2.addWidget(Color('red'))
        layout1_2.addWidget(Color('yellow'))
        layout1_2.addWidget(replot_btn)

        layout1_1.addLayout(layout1_2)

        # Second Row
        # Create Plot widget
        self.fig = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.fig)

        plot_menu = NavigationToolbar(self.canvas, self)
        
        layout1_1.addWidget(plot_menu)
        layout1_1.addWidget(self.canvas)
        

        # Row 3
        foo_btn = QPushButton("Foo", self)
        bar_btn = QPushButton("Bar", self)

        layout1_3.addWidget(foo_btn)
        layout1_3.addWidget(bar_btn)
        # Add Row 3 to Tab 1
        layout1_1.addLayout( layout1_3 )

        container1 = QWidget()
        container1.setLayout(layout1_1)





        # Tab 2
        layout2 = QVBoxLayout()
        
        # Row 1
        layout2_1 = QHBoxLayout()

        # Row 1 - Left
        layout2_1_left = QVBoxLayout()

        # Category list label
        cat_list_label = QLabel("Categories")
        layout2_1_left.addWidget(cat_list_label)
        # Category list
        self.cat_list = QListWidget()
        self.load_cat_list()
        layout2_1_left.addWidget(self.cat_list)

        # Add left side to Row 1 layout
        layout2_1.addLayout(layout2_1_left)

        # Row 1 - Right
        layout2_1_right = QVBoxLayout()

        # New category
        new_cat_label = QLabel("New Category")
        layout2_1_right.addWidget(new_cat_label)

        layout2_1_right_1= QHBoxLayout()
        # Row 1 - Right - Left
        layout2_1_right_1_left = QVBoxLayout()
        new_cat_label_1 = QLabel("Name:")
        new_cat_label_2 = QLabel("Colour:")
        self.new_cat_clear = QPushButton("Clear")

        self.new_cat_clear.clicked.connect(self.clear_new_category)

        layout2_1_right_1_left.addWidget(new_cat_label_1)
        layout2_1_right_1_left.addWidget(new_cat_label_2)
        layout2_1_right_1_left.addWidget(self.new_cat_clear)
        layout2_1_right_1.addLayout(layout2_1_right_1_left)

        # Row 1 - Right - Right
        layout2_1_right_1_right = QVBoxLayout()
        self.new_cat_input_1 = QLineEdit()
        self.new_cat_input_2 = QLineEdit()
        self.new_cat_submit = QPushButton("Submit")

        self.new_cat_submit.clicked.connect(self.submit_new_category)

        layout2_1_right_1_right.addWidget(self.new_cat_input_1)
        layout2_1_right_1_right.addWidget(self.new_cat_input_2)
        layout2_1_right_1_right.addWidget(self.new_cat_submit)
        layout2_1_right_1.addLayout(layout2_1_right_1_right)

        layout2_1_right.addLayout(layout2_1_right_1)

        # Edit category
        edit_cat_label = QLabel("Edit Category")
        layout2_1_right.addWidget(edit_cat_label)
        
        layout2_1_right_2 = QHBoxLayout()
        # Row 1 - Right - Left
        layout2_1_right_left = QVBoxLayout()
        edit_cat_label_1 = QLabel("Name:")
        edit_cat_label_2 = QLabel("Colour:")
        self.edit_cat_delete = QPushButton("Delete")

        layout2_1_right_left.addWidget(edit_cat_label_1)
        layout2_1_right_left.addWidget(edit_cat_label_2)
        layout2_1_right_left.addWidget(self.edit_cat_delete)
        layout2_1_right_2.addLayout(layout2_1_right_left)

        # Row 1 - Right - Right
        layout2_1_right_2_right = QVBoxLayout()
        self.edit_cat_input_1 = QLineEdit()
        self.edit_cat_input_2 = QLineEdit()
        self.edit_cat_submit = QPushButton("Submit")

        layout2_1_right_2_right.addWidget(self.edit_cat_input_1)
        layout2_1_right_2_right.addWidget(self.edit_cat_input_2)
        layout2_1_right_2_right.addWidget(self.edit_cat_submit)
        layout2_1_right_2.addLayout(layout2_1_right_2_right)

        layout2_1_right.addLayout(layout2_1_right_2)

        # Add right side to Row 1 layout
        layout2_1.addLayout(layout2_1_right)


        # Add Row 1 to Tab 2 layout
        layout2.addLayout(layout2_1)


        # Row 2
        # New topic
        new_topic_label = QLabel("Create New Topic")
        layout2.addWidget(new_topic_label)

        layout2_2 = QHBoxLayout()
 
        # Row 2 - Left
        layout2_2_left = QVBoxLayout()
        self.new_topic_label_1 = QLabel("Name:")
        self.new_topic_label_2 = QLabel("Category:")
        self.new_topic_label_3 = QLabel("Size:")
        self.new_topic_clear = QPushButton("Clear")

        self.new_topic_clear.clicked.connect(self.clear_new_topic)

        layout2_2_left.addWidget(self.new_topic_label_1)
        layout2_2_left.addWidget(self.new_topic_label_2)
        layout2_2_left.addWidget(self.new_topic_label_3)
        layout2_2_left.addWidget(self.new_topic_clear)
        layout2_2.addLayout(layout2_2_left)

        
        # Row 2 - Right
        layout2_2_right = QVBoxLayout()
        self.new_topic_input_1 = QLineEdit()
        self.new_topic_input_2 = QComboBox()
        self.new_topic_input_3= QSpinBox()
        self.new_topic_submit = QPushButton("Submit")

        # Category dropdown
        self.load_cat_dropdown_1()

        self.new_topic_input_3.setValue(1)
        self.new_topic_submit.clicked.connect(self.submit_new_topic)

        layout2_2_right.addWidget(self.new_topic_input_1)
        layout2_2_right.addWidget(self.new_topic_input_2)
        layout2_2_right.addWidget(self.new_topic_input_3)
        layout2_2_right.addWidget(self.new_topic_submit)
        layout2_2.addLayout(layout2_2_right)

        # Add Row 2 to Tab 2 layout
        layout2.addLayout(layout2_2)






        # Row 3
        layout2_3 = QHBoxLayout()

        # Row 3 - Left
        layout2_3_left = QVBoxLayout()

        # Topic list label
        topic_list_label = QLabel("Topics")
        layout2_3_left.addWidget(topic_list_label)
        # Topic list
        self.topic_list = QListWidget()
        self.load_topic_list()
        layout2_3_left.addWidget(self.topic_list)

        # Add left side to Row 3 layout
        layout2_3.addLayout(layout2_3_left)


        # Row 3 - Right
        layout2_3_right = QVBoxLayout()

        # Edit topic
        edit_topic_label = QLabel("Edit Topic")
        layout2_3_right.addWidget(edit_topic_label)
        
        # Row 3 - Right - 1
        layout2_3_right_1 = QHBoxLayout()
        edit_topic_label_1 = QLabel("Name:")
        edit_topic_input_1 = QLineEdit()
        
        layout2_3_right_1.addWidget(edit_topic_label_1)
        layout2_3_right_1.addWidget(edit_topic_input_1)
        # Row 3 - Right - 2
        layout2_3_right_2 = QHBoxLayout()
        edit_topic_label_2 = QLabel("Category:")
        self.edit_topic_input_2 = QComboBox()

        # Category dropdown
        self.load_cat_dropdown_2()

        layout2_3_right_2.addWidget(edit_topic_label_2)
        layout2_3_right_2.addWidget(self.edit_topic_input_2)
        # Row 3 - Right - 3
        layout2_3_right_3 = QHBoxLayout()
        edit_topic_label_3 = QLabel("Size:")
        edit_topic_input_3= QSpinBox()

        layout2_3_right_3.addWidget(edit_topic_label_3)
        layout2_3_right_3.addWidget(edit_topic_input_3)
        # Row 3 - Right - 4
        layout2_3_right_4 = QHBoxLayout()
        edit_topic_delete = QPushButton("Delete")
        edit_topic_submit = QPushButton("Submit")

        layout2_3_right_4.addWidget(edit_topic_delete)
        layout2_3_right_4.addWidget(edit_topic_submit)

        # Add rows to Row 3 right
        layout2_3_right.addLayout(layout2_3_right_1)
        layout2_3_right.addLayout(layout2_3_right_2)
        layout2_3_right.addLayout(layout2_3_right_3)
        layout2_3_right.addLayout(layout2_3_right_4)

        # Add right side to Row 3 layout
        layout2_3.addLayout(layout2_3_right)

        # Add Row 3 to Tab 2 layout
        layout2.addLayout(layout2_3)

        
        # Tab 2 Container
        container2 = QWidget()
        container2.setLayout(layout2)

        # Assign Tabs
        self.tabs.addTab(container1,'Display')
        self.tabs.addTab(container2,'Manage')

        self.setCentralWidget(self.tabs)


        # Menu
        rebuild_action = QAction("&Rebuild", self)
        rebuild_action.setStatusTip("Rebuild and populate the database.")
        rebuild_action.triggered.connect(rebuild)
        # Refresh topic and category lists on Tab 2
        rebuild_action.triggered.connect(self.load_topic_list)
        rebuild_action.triggered.connect(self.load_cat_list)
        rebuild_action.triggered.connect(self.load_cat_dropdown_1)
        rebuild_action.triggered.connect(self.load_cat_dropdown_2)

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(app.quit)
       
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(rebuild_action)
        file_menu.addAction(exit_action)
        





    def plot(self):

        # Sync Tables
        sync_tables()  
        # Create data array
        data = topic_data()

        # Clear old figure
        self.fig.clear()
        # Create an axis
        ax = self.fig.subplots()

        # Plot data
        # Compute circle positions:
        circles = circlify.circlify(
            data, 
            show_enclosure=False, 
            target_enclosure=circlify.Circle(x=0, y=0, r=1)
        )

        # Find axis boundaries
        lim = max(
            max(
                abs(circle.x) + circle.r,
                abs(circle.y) + circle.r,
            )
            for circle in circles
        )
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)

        # Print circle and labels for the topics (3rd level):
        for circle in circles:
            if circle.level != 3:
                continue
            x, y, r = circle

            label = circle.ex["id"]
            c = circle.ex["colour"]     
            ax.add_patch( plt.Circle((x, y), r*.988, linewidth=1.2, facecolor=c,edgecolor="black"))
            plt.annotate(label, (x,y ) ,va='center', ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5,alpha=.7),size=7)

        # Categories (2nd Level)
        legend_labels = []
        legend_icon = []
        for circle in circles:
            if circle.level != 2:
                continue
            x, y, r = circle

            label = circle.ex["id"]
            c = circle.ex["colour"]     

            # Legend Items
            legend_labels.append(label)
            legend_icon.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=12))
            
        
        # Create Legend
        ax.legend(legend_icon,legend_labels) 
        # Set figure tight layout
        self.fig.tight_layout()
        # Plot Labels
        # Remove axes
        ax.axis('equal')
        ax.tick_params(
            axis='both',        # affect both axis
            which='both',       # both major and minor ticks are affected
            bottom=False,       # ticks along the bottom edge are off
            left=False,         # ticks along the left edge are off
            labelbottom=False,  # labels along the bottom edge are off
            labelleft=False)    # labels along the left edge are off

        # Refresh canvas
        self.canvas.draw()

    def clear_new_topic(self):
        self.new_topic_input_1.setText("")
        self.new_topic_input_3.setValue(1)

    def clear_new_category(self):
        self.new_cat_input_1.setText("")
        self.new_cat_input_2.setText("")

    def submit_new_topic(self):
        name=self.new_topic_input_1.text()
        category=self.new_topic_input_2.currentText()
        size=self.new_topic_input_3.value()
        # Error Checking
        if name == "":
            QMessageBox.critical(self,"Error", "Topic name must not be empty.")
            return()
        elif size <= 0:
            QMessageBox.critical(self,"Error", "Topic size must be greater than zero")
            return()
        else:
            add_topic(name,category,size)
            self.clear_new_topic()
            self.load_topic_list()
            return()

    def submit_new_category(self):
        name=self.new_cat_input_1.text()
        colour=self.new_cat_input_2.text()

        # Error Checking
        if name == "":
            QMessageBox.critical(self,"Error", "Category name must not be empty.")
            return()
        else:
            add_category(name,colour)
            self.clear_new_category()
            self.load_cat_list()
            self.load_cat_dropdown_1()
            self.load_cat_dropdown_2()
            return()
    
    # Load category names into UI list
    def load_cat_list(self):
        self.cat_list.clear()
        for cat in fetch_category():
            self.cat_list.addItem(cat[1])
        self.cat_list.sortItems()

    # Load topic names into UI list
    def load_topic_list(self):
        self.topic_list.clear()
        for top in fetch_topic():
            self.topic_list.addItem(top[1])
        self.topic_list.sortItems()

    def load_cat_dropdown_1(self):
        self.new_topic_input_2.clear()
        for cat in fetch_category():
            self.new_topic_input_2.addItem(cat[1])

    def load_cat_dropdown_2(self):
        self.edit_topic_input_2.clear()
        for cat in fetch_category():
            self.edit_topic_input_2.addItem(cat[1])

# Main Function
def main():
    global app 
    app = QApplication(sys.argv)

    global window
    window = MainWindow()

    # Display window
    window.show()
    # Call plot function
    #window.plot()
    # GUI loop
    app.exec()






if __name__ == '__main__':
   main()