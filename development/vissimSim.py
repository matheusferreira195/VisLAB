import pandas as pd
import sqlite3
import itertools as it
import numpy as np
import win32com.client as com
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import glob
import os

cnx = sqlite3.connect(r'E:\Google Drive\Scripts\vistools\resources\vislab.db')#, isolation_level=None)
cursor = cnx.cursor()


if __name__ == "__main__":

    vissim_simulation(experiment)

