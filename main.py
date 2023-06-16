# Import Libraries
import sys
import logging


import circlify

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from mysql.connector import connect, Error

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QAction



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
        
    # Connect to db
    mysql_connect(query,values)

# Function to create new entry to category table
def add_category(name,colour):

    query = "INSERT INTO category (name, colour) VALUES (%s,%s)"
    values = (name, colour)

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


def display_tables():
    # Connect to mySQL database
    try:
        with connect(
            host="localhost",
            user="admin",
            password="admin",
            database="fixations"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                for db in cursor:
                    print(db)

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

    print("Current Tables:")
    display_tables()
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
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)



        # Tab 1
        layout1_1 = QVBoxLayout()
        layout1_2 = QHBoxLayout()
        layout1_3 = QHBoxLayout()

        layout1_1.setContentsMargins(0,0,0,0)
        layout1_1.setSpacing(5)

        # First Row

        # Button connected to 'plot' method to replot figure
        replot_btn = QPushButton(QIcon("refresh.png"), "Refresh Plot", self)
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
        

        # Third Row
        foo_btn = QPushButton("Foo", self)
        bar_btn = QPushButton("Bar", self)
        bar_btn.clicked.connect(topic_data)
        bar_btn.clicked.connect(app.quit)
   

        layout1_3.addWidget(foo_btn)
        layout1_3.addWidget(bar_btn)

        layout1_1.addLayout( layout1_3 )

        container1 = QWidget()
        container1.setLayout(layout1_1)


        # Tab 2
        layout2 = QVBoxLayout()
        
        # First Row
        layout2_1 = QHBoxLayout()
            # First Row - Left
        layout2_1_left = QVBoxLayout()
                # New Category
        layout2_1_left.addWidget(Color('red'))
                # New Topic
        layout2_1_left.addWidget(Color('red'))

 
        layout2_1.addLayout(layout2_1_left)



            # First Row - Right
        layout2_1_right = QVBoxLayout()
                # Widget
        layout2_1_right.addWidget(Color('yellow'))
        layout2_1_right.addWidget(Color('yellow'))
        layout2_1_right.addWidget(Color('yellow'))

 
        layout2_1.addLayout(layout2_1_right)




        layout2.addLayout(layout2_1)

        # Second Row
        layout2.addWidget(Color('green'))
        layout2.addWidget(Color('blue'))

        container2 = QWidget()
        container2.setLayout(layout2)

        # Assign Tabs
        tabs.addTab(container1,'Display')
        tabs.addTab(container2,'Manage')

        self.setCentralWidget(tabs)

        # Menu
        dump_action = QAction("&Delete All", self)
        dump_action.setStatusTip("Delete all tables and entries.")
        dump_action.triggered.connect(dump_all)

        rebuild_action = QAction("&Rebuild", self)
        rebuild_action.setStatusTip("Rebuild and populate the database.")
        rebuild_action.triggered.connect(rebuild)

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(app.quit)
       
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(dump_action)
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
            ax.add_patch( plt.Circle((x, y), r, linewidth=1.2, facecolor=c,edgecolor="black"))
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



app = QApplication(sys.argv)

window = MainWindow()
# Display window
window.show()
# Call plot function
window.plot()

# GUI loop
app.exec()





