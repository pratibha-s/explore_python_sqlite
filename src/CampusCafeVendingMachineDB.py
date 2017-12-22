#!/usr/local/bin/python3.6

'''
Created on Jun 6, 2016

@author: pratibhasharma
'''
import sqlite3

__version__ = '0.1'

class CampusCafeVendingMachineDB():
    '''
    classdocs: Database to keep the cafe user's personal information, expense profile and dietary profile
    '''


    def __init__(self, **kwargs):
        '''
        Constructor: Create database if doesn't exists, Create tables and populate data
        '''
        self.filename = kwargs.get('filename', 'online_cafe.db')
        
        self.user_table = kwargs.get('usertable', 'UserTable')
        self.amenity_table = kwargs.get('amenitytable', 'AmenityTable')
        self.amenity_menu_table = kwargs.get('amenitymenutable', 'AmenityMenuTable')
        self.food_item_table = kwargs.get('fooditemtable', 'FoodItemTable')
        self.order_table = kwargs.get('ordertable', 'OrderTable')
#         self.expense_profile_table = kwargs.get('expensetable', 'ExpenseProfileTable')
#         self.dietary_profile_table = kwargs.get('dietarytable', 'DietaryProfileTable')
        
        self.db = sqlite3.connect(self.filename)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.db.execute(''' CREATE TABLE IF NOT EXISTS {}
                            (User_Name TEXT  COLLATE NOCASE , Card_Number TEXT, Family_Code TEXT, 
                             Password TEXT, Balance REAL, Calories SMALLINT )
                            '''.format(self.user_table))
        
        self.db.execute(''' CREATE TABLE IF NOT EXISTS {}
                            (Amenity_Id SMALLINT, Amenity_type TEXT, 
                             Amenity_Name TEXT  COLLATE NOCASE , Amenity_Adress TEXT  )
                            '''.format(self.amenity_table))

        
        self.db.execute(''' CREATE TABLE IF NOT EXISTS {}
                            (Amenity_Id TEXT, Food_Item_Id TEXT)
                            '''.format(self.amenity_menu_table))
        

        self.db.execute(''' CREATE TABLE IF NOT EXISTS {}
                            (Food_Item_Id SMALLINT, Food_Item_Name TEXT  COLLATE NOCASE , 
                            Food_Item_Calories SMALLINT)
                            '''.format(self.food_item_table))
                        
                        
        self.db.execute(''' CREATE TABLE IF NOT EXISTS {}
                            (User_Name TEXT  COLLATE NOCASE , Card_Number TEXT, 
                            Family_Code TEXT, Amenity_Name SMALLINT  COLLATE NOCASE , 
                            Food_Item_Name SMALLINT  COLLATE NOCASE , Calories_Consumed SMALLINT, 
                            Amount_Spent REAL, Order_Date DATETIME)
                            '''.format(self.order_table))
        

    def __iter__(self):
        """
        Return generator object with dicts of entire DB contents
        """
        cursor = self.db.execute('SELECT * FROM {} ORDER BY Date, Time'.format(self.user_table))
        for row in cursor: yield dict(row)
                        
  
    def get_cafe_list(self):
        return(self.get_amenity_list("CAFE"))
        

    def get_vending_machine_list(self):
        return(self.get_amenity_list("VendingMachine"))
        

    def get_amenity_list(self, atype):
        atype = (atype,)
        t = [(dict(row)["Amenity_Name"]) for row in 
             self.cursor.execute("SELECT Amenity_Name FROM AmenityTable WHERE Amenity_type = ?", (atype))]
        if (t):
            return (t)
        return 0



    def verify_user_login(self, user_name, passwd, card_no, family_code):
        
        try:
            self.cursor.execute('''SELECT User_Name FROM {tn} WHERE  
                             User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_code=? and Password=?'''.
                                format(tn=self.user_table), (user_name, card_no, family_code, passwd))
            userdata = self.cursor.fetchone()
            if (userdata):
                return True
        except sqlite3.Error as e:
                print ("verify_user_login:An error occurred:", e.args[0])
        return False


        # Add entry in order table, an entry in expense table, an entry in dietary table, update user table
        # 
        # order_table:  User_Name TEXT,        Card_Number TEXT, 
        #               Family_Code TEXT,      Amenity_Name SMALLINT, 
        #               Food_Item_Name SMALLINT, Calories_Consumed SMALLINT, 
        #               Amount_Spent REAL,     Order_Date DATETIME
        #
        # User table: User_Name TEXT, Card_Number TEXT, Family_Code TEXT, Password TEXT, Balance REAL, Calories SMALLINT
    def update_tables_with_orders_info(self, user_name, passwd, card_no, family_code,
                                  amenity_id, food_items,
                                  amt_spent, calories_consumed, order_date
                                  ):
               
        
        cost_of_items=0.00
        calories_in_items=0
        for item in food_items:
            cost_of_items = cost_of_items + item['Food_Item_Price']
            calories_in_items = calories_in_items + item['Food_Item_Calories']
            
            
        self._add_orders_in_ordertable(user_name, card_no, family_code,
                                       amenity_id, food_items, order_date)
        self._update_balance_in_usertable(user_name, passwd, card_no, family_code,  cost_of_items)
            
    
    # order_table:  User_Name TEXT, Card_Number TEXT, 
    #               Family_Code TEXT,      Amenity_Name SMALLINT, 
    #               Food_Item_Name SMALLINT, Calories_Consumed SMALLINT, 
    #               Amount_Spent REAL, Order_Date DATETIME
    def _add_orders_in_ordertable(self, user_name, card_no, family_code,
                                       amenity_name, food_items,
                                    order_date):
        try:
            for item in food_items:
                self.cursor.execute('''INSERT INTO {tn} VALUES (?,?,?,?,?,?,?,?) 
                                 '''.format(tn=self.order_table),
                                 (user_name, card_no, family_code, str(amenity_name),
                                  str(item['Food_Item_Name']), str(item['Food_Item_Calories']),
                                  item['Food_Item_Price'], order_date))
            self.db.commit()
        except sqlite3.Error as e:
                print ("_add_orders_in_ordertable:An error occurred:", e.args[0])
    
    
    def _get_orders_for_user(self, user_name, card_no, family_code):
        try:
            self.cursor.execute('''SELECT * FROM {tn} WHERE  
                             User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_code=?'''.
                                format(tn=self.order_table), (user_name, card_no, family_code))
            self.db.commit()
        except sqlite3.Error as e:
                print ("_get_orders_for_user:An error occurred:", e.args[0])
        orders_data = self.cursor.fetchall()
        if (orders_data):
            for row in orders_data:
                yield (dict(row))
    
   
    def get_user_balance(self, user_name, passwd, card_no, family_code):
        try:
            self.cursor.execute('''SELECT Balance FROM {tn} WHERE  
                             User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_code=? and Password=?'''.
                                format(tn=self.user_table), (user_name, card_no, family_code, passwd))
            userdata = self.cursor.fetchone()
            if (userdata):
                userdata = dict(userdata)
                return(userdata['Balance'])
        except sqlite3.Error as e:
                print ("get_user_balance:An error occurred:", e.args[0])
    

    def get_user_calorie_plan(self, user_name, passwd, card_no, family_code):
        try:
            self.cursor.execute('''SELECT Calories FROM {tn} WHERE  
                             User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_code=? and Password=?'''.
                                format(tn=self.user_table), (user_name, card_no, family_code, passwd))
            userdata = self.cursor.fetchone()
            if (userdata):
                userdata = dict(userdata)
                return(userdata['Calories'])
        except sqlite3.Error as e:
                print ("get_user_calorie_plan:An error occurred:", e.args[0])
    

    def _update_balance_in_usertable(self, user_name, passwd, card_no, family_code, 
                                          amt_spent):
        try:
            self.cursor.execute('''SELECT Balance FROM {tn} WHERE 
                                User_Name=? COLLATE NOCASE and Password=? and 
                                Card_Number=? and Family_Code=?'''.
                                format(tn=self.user_table), (user_name, passwd, card_no, family_code))
            user_data = dict(self.cursor.fetchone())
            user_data['Balance'] = user_data['Balance'] - amt_spent
            self.cursor.execute('''UPDATE {tn} SET Balance = ?  WHERE  
                             User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_Code=? and Password=?
                             '''.format(tn=self.user_table), (user_data['Balance'], user_name, card_no, family_code, passwd))
            self.db.commit()
        except sqlite3.Error as e:
                print ("_update_balance_in_usertable:An error occurred:", e.args[0])
    
    
    
    def add_more_funds_in_usertable(self, user_name, passwd, card_no, family_code, 
                                          additional_amt):      
        try:
            self.cursor.execute('''SELECT Balance FROM {tn} WHERE  
                             User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_Code=? and Password=?'''.
                                format(tn=self.user_table), (user_name, card_no, family_code, passwd))
            user_data = dict(self.cursor.fetchone())
            user_data['Balance'] = user_data['Balance'] + float(additional_amt)
            
            self.cursor.execute('''UPDATE {tn} SET Balance = ? WHERE  
                             User_Name = ?  COLLATE NOCASE and Password=? and Card_Number = ? and Family_Code=? 
                             '''.format(tn=self.user_table), (user_data['Balance'], user_name, passwd, card_no, family_code))
            self.db.commit()
        except sqlite3.Error as e:
                print ("add_more_funds_in_usertable:An error occurred:", e.args[0])
    
    
    def update_diet_plan_in_usertable(self, user_name, passwd, card_no,
                                      family_code, new_diet_plan):
        try:
            self.cursor.execute('''UPDATE {tn} SET Calories = ? WHERE  
                             User_Name = ?   COLLATE NOCASE and Password=? and Card_Number = ? and Family_Code=?
                             '''.format(tn=self.user_table), (new_diet_plan, user_name, passwd, card_no, family_code))
            self.db.commit()
        except sqlite3.Error as e:
                print ("add_more_funds_in_usertable:An error occurred:", e.args[0])
    
    
    def get_menu_items(self, amenity_name):
        self.cursor.execute('''select Food_Item_Id, Food_Item_Name, Food_Item_Price, 
                                Food_Item_Calories From {ft} where 
                                Food_Item_Id in (SELECT Food_Item_Id FROM {amt} where Amenity_Id in (
                                        Select Amenity_Id from {at} where Amenity_Name = ?  COLLATE NOCASE ))'''
                                        .format(ft="FoodItemTable", amt="AmenityMenuTable", at="AmenityTable"),
                                        (amenity_name,))

        rows = self.cursor.fetchall()
        rowdata = []
        for row in rows:
            rowdata.append(dict(row))
        return(rowdata)
    
    
    # add all default rows in the tables and delete rest
    # 
    def reset_tables(self):
        try:
            self.cursor.execute('''DELETE FROM {tn} 
                                 '''.format(tn=self.order_table))
            self.cursor.execute('''DELETE FROM {tn} 
                                 '''.format(tn=self.user_table))
            self.db.commit()

            usersdata = {'1':{'User_Name':'ps', 'Card_Number':'ps',
                             'Family_Code':'ps', 'Password':'ps',
                             'Balance':'500', 'Calories':'1500'},
                        '2':{'User_Name':'hexel', 'Card_Number':'200',
                             'Family_Code':'00', 'Password':'200',
                             'Balance':'800', 'Calories':'2500'},
                        '3':{'User_Name':'veyron', 'Card_Number':'300',
                             'Family_Code':'00', 'Password':'300',
                             'Balance':'800', 'Calories':'2000'}
                         
                        }
            
            for urecord in usersdata.keys():
                self.db.execute(''' INSERT INTO {} 
                                (User_Name, Card_Number, Family_Code, 
                                 Password, Balance, Calories) 
                                 VALUES (?,?,?,?,?,?)'''.format(self.user_table),
                                                             (usersdata[urecord]['User_Name'],
                                                              usersdata[urecord]['Card_Number'],
                                                              usersdata[urecord]['Family_Code'],
                                                              usersdata[urecord]['Password'],
                                                              usersdata[urecord]['Balance'],
                                                              usersdata[urecord]['Calories']
                                                            )
                            )
            self.db.commit()
        except sqlite3.Error as e:
            print ("reset_tables:An error occurred:", e.args[0])
    
            
    def select_star_from_all_tables(self):
        alltables = (self.amenity_menu_table, self.amenity_table, self.food_item_table,
                     self.user_table, self.order_table)
        for table in (alltables):
            print(table)
            for row in (self.cursor.execute('''SELECT * FROM {tn}'''.
                                 format(tn=table))):
                print(dict(row))
    
    
    def general_call(self):
        nm = "ps"
        card_no = "ps"
        family_code = "ps"
        passwd = "ps"
        for row in (self.cursor.execute('''SELECT User_Name FROM {tn} WHERE  
                            User_Name = ?  COLLATE NOCASE and Card_Number = ? and Family_code=? and Password=?'''.
                                 format(tn=self.user_table), (nm, card_no, family_code, passwd))):
            print(dict(row))

# Populate data in the tables
    def populate_data(self):
#--------------------- USERS TABLE -------------------------------------------------        

        usersdata = {'1':{'User_Name':'ps', 'Card_Number':'ps',
                             'Family_Code':'ps', 'Password':'ps',
                             'Balance':'500', 'Calories':'1500'},
                        '2':{'User_Name':'hexel', 'Card_Number':'200',
                             'Family_Code':'00', 'Password':'200',
                             'Balance':'800', 'Calories':'2500'},
                        '3':{'User_Name':'veyron', 'Card_Number':'300',
                             'Family_Code':'00', 'Password':'300',
                             'Balance':'800', 'Calories':'2000'}
                    }
        
        for urecord in usersdata.keys():
            self.db.execute(''' INSERT INTO {} 
                            (User_Name, Card_Number, Family_Code, 
                             Password, Balance, Calories) 
                             VALUES (?,?,?,?,?,?)'''.format(self.user_table),
                                                         (usersdata[urecord]['User_Name'],
                                                          usersdata[urecord]['Card_Number'],
                                                          usersdata[urecord]['Family_Code'],
                                                          usersdata[urecord]['Password'],
                                                          usersdata[urecord]['Balance'],
                                                          usersdata[urecord]['Calories']
                                                        )
                        )

#--------------- Amenities Data --------------------------------------------------------        
        
        amenity_data = {'1':{'Amenity_Id': '1', 'Amenity_type':'CAFE',
                             'Amenity_Name':'SmartCafe', 'Amenity_Adress':'123 first lane'},
                        '2':{'Amenity_Id': '2', 'Amenity_type':'CAFE',
                             'Amenity_Name':'OldCafe', 'Amenity_Adress':'125 first lane'},
                        '3':{'Amenity_Id': '3', 'Amenity_type':'VendingMachine',
                             'Amenity_Name':'SodaMachine', 'Amenity_Adress':'127 first lane'},
                         }
        

  
    def close(self):
        """
        Safely close down the database
        """
        self.db.close()
        del self.filename
        
        
        
if __name__ == '__main__':
    pass

