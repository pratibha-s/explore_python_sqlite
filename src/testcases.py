'''
Created on Aug 19, 2016

@author: pratibhasharma
'''
import cafeOnlineDB
from datetime import date, time, datetime
from tkinter import *

from tkinter import ttk
from time import sleep
from re import split

master = Tk()  
v = StringVar()

def rsel():
    print(v.get())  


def main():
    database = cafeOnlineDB.cafeOnlineDB()
    
    user_name="ps"
    passwd = "ps"
    card_no= "ps"
    family_code = "ps"
    if (database.verify_user_login(user_name, passwd, card_no, family_code)):
        print("---Found user: "+user_name+"\n\n")
        pass
    
    dt = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")

    x = database._get_orders_for_user(user_name, card_no, family_code)
    
    print("Order History for User: "+user_name)
    for order in x:
        (dt,tm) = split(" ",order['Order_Date'])
        print(dt)
        print("{:20}".format(order['Order_Date']), " " , 
              "{:21}".format(order['Food_Item_Name']), " ", 
              "{:>6}".format(order['Calories_Consumed']), " ", 
              "${:>7.2f}".format(order['Amount_Spent'])
              )

    # Reset data from tables.
#     print("---Reset all tables data to default values---")
#     database.reset_tables()
    
    print("---Display data from all tables---")
    database.select_star_from_all_tables()

    database.close()
    
if __name__ == '__main__':
    main()

