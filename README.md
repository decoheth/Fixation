# Fixation

Fixation is a project designed to visually represent different interests I have, and how long I am invested in them. Fixation makes use of a hierarchal circle packing algorithm to group the topics.

### Example

![](https://github.com/decoheth/Fixation/blob/master/static/Figure_1.png)

### Used tools:
* [circlify](https://github.com/elmotec/circlify/) - Python implementation of a circle packing layout algorithm.
* [matplotlib](https://matplotlib.org) - Python library for visualisation.
* [MySQL](https://www.mysql.com/) - Database management system used for data storage.
* [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/) - Python driver for communicating with MySQL servers.
* [PyInstaller](https://pyinstaller.org/en/stable/) - PyInstaller bundles a Python application into an executable.   
* [PyQt5](https://pypi.org/project/PyQt5/) - Python GUI framework.

## Usage

Download/clone repository and launch fixation.exe application.

Install MySQL client on local machine to handle server connections.


## Usage - Dev

Using pip, install the project requirements:

```python
    pip install -r requirements.txt
```

To build a new executable, run:

```python
    pyinstaller --onefile -w fixation.py
```
This wil generate the appropriate files and folders to generate the executable. The resultant fixation.exe file will be found in the newly created dist/ folder. Copy this file into the main folder and overwrite the previous fixation.exe executable. To launch the executable from elsewhere, right click on fixation.exe and select 'Create Shortcut.'