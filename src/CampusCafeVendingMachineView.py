#!/usr/local/bin/python3.6

from tkinter import *
from datetime import datetime
from tkinter import ttk

import CampusCafeVendingMachineDB as DB
import messagebox




__version__ = '0.1'

class CampusCafeVendingMachineView:

    def __init__(self, master):
        '''
        Constructor
        '''
        self.bgcolor = '#CCCCFF'
        
        self.style = ttk.Style()
        self.style.configure('TFrame',        background=self.bgcolor)
        self.style.configure('TButton',       background=self.bgcolor, font= ('Arial Black', 12))
        self.style.configure('TLabel',        background=self.bgcolor, font= ('Arial Black', 12))
        self.style.configure('Status.TLabel', background=self.bgcolor, font= ('Arial Black', 12))
        self.style.configure('Result.TLabel', background=self.bgcolor, font= ('Arial Black', 12))

        self.total_expenditure=0
        self.total_calories=0
        self.item_vars = []
        self.uname  = StringVar()
        self.ucard  = StringVar()
        self.ufcode = StringVar()
        self.upass  = StringVar()
        self.master = master
        
        self.database = DB.CampusCafeVendingMachineDB()
        self._create_GUI()
        self.master.protocol("WM_DELETE_WINDOW", self._close_DB_and_GUI)

   
    def _close_DB_and_GUI(self):
        self.database.close()
        self.master.destroy()
    

    def _create_GUI(self):
        self.master.configure(background=self.bgcolor,borderwidth=5, relief = SUNKEN)
        self.master.title('CafeOnline')
        self.master.geometry('705x705+350+90')
        self.master.resizable(False, False)
        ttk.Label(self.master, text="Welcome to CafeOnline",font= ('Arial Black', 30)).place(x=180,y=380)
        

        self.notebook = ttk.Notebook(self.master)
        self.notebook.place(x=1, y=1,height=140,width=700)
        self.frame_cafe_list = ttk.Frame(self.notebook,borderwidth=5,relief = SUNKEN)
        self.frame_vending_machine_list   = ttk.Frame(self.notebook,borderwidth=5,relief = SUNKEN)
        self.frame_myinfo_login = ttk.Frame(self.notebook,borderwidth=5,relief = SUNKEN)
        self.notebook.add(self.frame_cafe_list, text="Cafe")
        self.notebook.add(self.frame_vending_machine_list,   text = "VM")
        self.notebook.add(self.frame_myinfo_login, text = "My Account")
        
        self.amenity_type=""
        self._create_vending_machine_GUI()
        self._create_cafe_GUI()
        self._create_myaccount_GUI()
     
#--------------------------------------------------------------------------
#-------------------- cafe GUI --------------------------------------------
#--------------------------------------------------------------------------
    def _create_cafe_GUI(self):
        ttk.Label(self.frame_cafe_list, text="Select Cafe from the List").grid(row=0, column=0, padx=9,sticky='e')
        print("in _create_cafe_GUI: calling setup_combobox_frame")
        (self.cafe_combobox, 
         self.cafe_select_button, 
         self.cafe_list, 
         self.selected_cafe   ) = self.setup_combobox_frame(self.frame_cafe_list, "CAFE")


#--------------------------------------------------------------------------
#--------------------- VM GUI ---------------------------------------------
#--------------------------------------------------------------------------
    def _create_vending_machine_GUI(self):
        ttk.Label(self.frame_vending_machine_list, text="Select Vending Machine").grid(row=0, column=0, padx=9,sticky='e')
        print("in _create_vending_machine_GUI: calling setup_combobox_frame1")
        (self.vending_machine_combobox, 
         self.vending_machine_select_button, 
         self.vending_machine_list, 
         self.selected_vending_machine) = self.setup_combobox_frame(self.frame_vending_machine_list, "VendingMachine")



    def setup_combobox_frame(self, frame_amenity, amenity_type):
        print("setup_combobox_frame: amenity_type: ", amenity_type)
        
        amenity_list = self.database.get_amenity_list(amenity_type)
        selected_amenity = StringVar()
        combobox = ttk.Combobox(frame_amenity, state='readonly', 
                                         textvariable=selected_amenity, 
                                         values=amenity_list)
        combobox.grid(row=1, column=0,padx=6,sticky='e')
        combobox.focus()
        combobox.current(0)
        print("in setup_combobox_frame: selected_amenity: ", selected_amenity.get())
        button = ttk.Button(frame_amenity, text='OK', 
                                                    command=lambda: self._display_amenity_menu())
        button.grid(row=1,column=1,padx=3)
        return (combobox, button, amenity_list, selected_amenity)


    
    

    def _display_amenity_menu(self):
        
        # Check which tab is selected and set the amenity type accordingly
        # Amenity_type will determine menuitem of which amenity will be displayed
        selected_amenity=""
        if self.notebook.index(self.notebook.select())== 0:
            self.amenity_type="CAFE"
            selected_amenity = self.selected_cafe.get()
            self.cafe_select_button.state(['disabled'])
            self.cafe_combobox.state(['disabled'])
            self.notebook.tab(1, state='disabled')
        
        if self.notebook.index(self.notebook.select())== 1:
            self.amenity_type="VendingMachine"
            selected_amenity=self.selected_vending_machine.get()
            self.vending_machine_select_button.state(['disabled'])
            self.vending_machine_combobox.state(['disabled'])
            self.notebook.tab(0, state='disabled')
        
        self.notebook.tab(2, state= 'disabled')
        
        print(self.amenity_type," :  ", self.notebook.index(self.notebook.select()))
        self.frame_amenity_menu=ttk.Frame(self.master,relief = SUNKEN)
        self.frame_amenity_menu.place(x=1,y=141,height=700, width=700)
        ttk.Label(self.frame_amenity_menu, text="Welcome to "+selected_amenity).place(x=210,y=2)
        ttk.Label(self.frame_amenity_menu, 
                  text="Menu Items to Select: ").place(x=10,y=30)

        self.frame_amenity_cbutton_items = ttk.Frame(self.frame_amenity_menu,relief=SUNKEN)
        self.frame_amenity_cbutton_items.place(x=10,y=80,height=435,width=678)
        print("_display_amenity_menu: ", selected_amenity)
        self.menu_items = self.database.get_menu_items(selected_amenity) # Database Function
        
        self.yposition=10
        self.yinterval=25
        self.xinterval=15
        
        # if CAFE then display complete menu checkbuttons form
        if self.amenity_type=="CAFE":
            self.item_vars= [IntVar() for self.item_ctr in range(len(self.menu_items))]
            self.item_ctr = 0
            for row in self.menu_items:
                self.item_details = str(row['Food_Item_Name']) +"\t"+str(row['Food_Item_Price'])+"\t" +str(row['Food_Item_Calories'])
    
                ttk.Checkbutton(self.frame_amenity_cbutton_items, variable= self.item_vars[self.item_ctr], 
                                text=self.item_details, command=lambda: self._next_amenity_button_state()
                                ).place(x=self.xinterval,y=self.yposition)
                self.yposition=self.yposition+self.yinterval  
                self.item_ctr=self.item_ctr+1
                
        # if VendingMachine, display complete menu in radiobutton form, so user can select one item to dispense
        if self.amenity_type=="VendingMachine":
            self.item_vars = [IntVar()]
            for row in self.menu_items:
                self.item_details = str(row['Food_Item_Name']) +"\t"+str(row['Food_Item_Price'])+"\t" +str(row['Food_Item_Calories'])
    
                ttk.Radiobutton(self.frame_amenity_cbutton_items, variable= self.item_vars[0], 
                                text=self.item_details, command=lambda: self._next_amenity_button_state(), 
                                value=row['Food_Item_Id']
                                ).place(x=self.xinterval,y=self.yposition)
                self.yposition=self.yposition+self.yinterval  
      
      
        ttk.Button(self.frame_amenity_menu, text='CANCEL', 
                   command=lambda: self._cancel_amenity_menu_selection()).place(x=300,y=520)
        self.amenity_menu_next_button = ttk.Button(self.frame_amenity_menu, text='NEXT', 
                                                command=lambda: self._display_amenity_order_details(self.amenity_type))
        self.amenity_menu_next_button.place(x=400, y=520)
        self.amenity_menu_next_button.state(['disabled'])




     
    # "NEXT" button is disabled by default. Enabled it if atleast one menuitem is selected
    def _next_amenity_button_state(self):
        
        self.menu_item_button_selected=0
        for self.item_var in self.item_vars:
            if self.item_var.get():
                self.menu_item_button_selected=1
                break
            
        if ( self.menu_item_button_selected==1 ):
            self.amenity_menu_next_button.state(['!disabled'])
        else:
            self.amenity_menu_next_button.state(['disabled'])

    
    
    # Items have been selected, display confirmation screen to provide payment info
    def _display_amenity_order_details(self, amenity_type):
        
        selected_amenity=""
        if self.amenity_type=="CAFE":
            selected_amenity = self.selected_cafe.get()
        if self.amenity_type=="VendingMachine":
            selected_amenity = self.selected_vending_machine.get()

        self.frame_amenity_order = ttk.Frame(self.master,relief = SUNKEN)
        self.frame_amenity_order.place(x=1,y=141,height=700,width=700)
        
        ttk.Label(self.frame_amenity_order, text="Welcome to "+selected_amenity).place(x=210,y=2)
        ttk.Label(self.frame_amenity_order, 
                  text="Please verify your order and provide payment information then press 'Order Now!': \n"
                  ).place(x=10,y=30)
        
        ttk.Separator(self.frame_amenity_order).place(x=2,y=80,width=700,height=3)
        self.yposition= 90
        self.yinterval= 18
        self.item_ctr=0
        self.selected_items = []
        print(self.item_vars)
        ttk.Label(self.frame_amenity_order, text='Item Name', font= ('Arial', 12)
                  ).place(x=10,y=60)
        ttk.Label(self.frame_amenity_order, text='Calories', font= ('Arial', 12)
                  ).place(x=150,y=60)
        ttk.Label(self.frame_amenity_order, text='Price', font= ('Arial', 12)
                  ).place(x=250,y=60)
                  
        
        if self.amenity_type=="CAFE":
            for row in self.menu_items:
                if (self.item_vars[self.item_ctr].get()==1):
                    self.item_details = str(row['Food_Item_Name']
                                            ) +"\t"+str(row['Food_Item_Calories']
                                                        )+"\t"+str(row['Food_Item_Price']
                                                        )
                    ttk.Label(self.frame_amenity_order, text=str(row['Food_Item_Name']), font= ('Arial', 12)
                              ).place(x=10,y=self.yposition)
                    ttk.Label(self.frame_amenity_order, text=str(row['Food_Item_Calories']), font= ('Arial', 12)
                              ).place(x=150,y=self.yposition)
                    ttk.Label(self.frame_amenity_order, text=str(row['Food_Item_Price']), font= ('Arial', 12)
                              ).place(x=250,y=self.yposition)
                    self.yposition = self.yposition +self.yinterval
                    self.selected_items.append(row)
                self.item_ctr= self.item_ctr+1


        if self.amenity_type=="VendingMachine":
            for row in self.menu_items:
                if (self.item_vars[0].get()==row['Food_Item_Id']):
                    self.item_details = str(row['Food_Item_Name']
                                            ) +"\t"+str(row['Food_Item_Calories']
                                                        )+"\t"+str(row['Food_Item_Price']
                                                        )
                    self.todays_vm_calories=row['Food_Item_Calories']
                    self.todays_vm_price = row['Food_Item_Price']
                    ttk.Label(self.frame_amenity_order, text=str(row['Food_Item_Name']), font= ('Arial', 12)
                              ).place(x=10,y=self.yposition)
                    ttk.Label(self.frame_amenity_order, text=str(row['Food_Item_Calories']), font= ('Arial', 12)
                              ).place(x=150,y=self.yposition)
                    ttk.Label(self.frame_amenity_order, text=str(row['Food_Item_Price']), font= ('Arial', 12)
                              ).place(x=250,y=self.yposition)
                    self.yposition = self.yposition +self.yinterval
                    self.selected_items.append(row)
            
            ttk.Separator(self.frame_amenity_order).place(x=3,y=self.yposition,width=700,height=3)
            self.yposition = self.yposition +10
           
            ttk.Label(self.frame_amenity_order, text='Total',
                      ).place(x=10,y=self.yposition)
            ttk.Label(self.frame_amenity_order, text=str(self.get_todays_calories())+" Cal"
                      ).place(x=150,y=self.yposition)
            ttk.Label(self.frame_amenity_order, text="$"+str(self.get_todays_expenditure())
                      ).place(x=250,y=self.yposition)
                
                
        # ------- Display Login  and payment information -----------
        # ----- Create payment frame and display widgets for payment information ----
        fc = [(1,445), (70,700)]
        wc = [(10,5),(115,5),(350,5),(455,5),(10,35),(115,35),(350,35),(455,35)]
        wfont = "Arial Black"
        fontsize = 12

        self.frame_amenity_user_login = ttk.Frame(self.frame_amenity_order,relief=SUNKEN)
        self.frame_amenity_user_login.place(x=fc[0][0],y=fc[0][1],height=fc[1][0],width=fc[1][1])
        self.display_login_info(self.frame_amenity_user_login, wc, wfont, fontsize)

        self.cafe_order_back_button = ttk.Button(self.frame_amenity_order, text="BACK", 
                                                 command=self._backto_menu_selection)
        self.cafe_order_back_button.place(x=300,y=520)
        self.cafe_order_cancel_button = ttk.Button(self.frame_amenity_order, text="CANCEL", 
                                                   command=lambda: self._cancel_the_order())
        self.cafe_order_cancel_button.place(x=400,y=520)
        self.cafe_order_now_button = ttk.Button(self.frame_amenity_order, text="Order Now!", 
                                                 command=lambda: self._place_the_order())
        self.cafe_order_now_button.place(x=500,y=520)

    
    
    def _backto_menu_selection(self):
        self.frame_amenity_order.destroy()
    

    def get_todays_expenditure(self):
        self.todays_price=0
        
        for menu_item in self.selected_items:
            self.todays_price = self.todays_price + menu_item['Food_Item_Price']
        print("Total Expense: ", self.todays_price)
        return self.todays_price

         

    def get_todays_calories(self):
        self.todays_calories=0
        for menu_item in self.selected_items:
            self.todays_calories = self.todays_calories + menu_item['Food_Item_Calories']
        print("Total Calories: ", self.todays_calories)
        return self.todays_calories
    


    def _place_the_order(self):
        selected_amenity=""
        if self.amenity_type=="CAFE":
            selected_amenity = self.selected_cafe.get()
        if self.amenity_type=="VendingMachine":
            selected_amenity = self.selected_vending_machine.get()
        if not (self.uname.get() and self.ucard.get() and 
                self.ufcode.get() and self.upass.get()):
            messagebox.showerror(title="Userinfo incomplete", 
                                 message= "Please provide userinfo, password, card no and family code and try again")
            return
            
        if (self._verify_user_login() == False) :
            messagebox.showerror(title="User does not exist", 
                                 message= "Username or card number or password is invalid. Please try again")
            return 0
        
        if (not self.verify_user_funds()):
            messagebox.showerror(title="Insufficient funds", 
                                 message= "User does not have enough funds in his account. Please add more funds")
            return 0
            
        self.order_datetime = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
        print("Todays Expense ", self.get_todays_expenditure()) 

        self.order_status = self.database.update_tables_with_orders_info(self.uname.get().lower(), 
                                                            self.upass.get(), 
                                                            self.ucard.get(), 
                                                            self.ufcode.get(),
                                                            selected_amenity.lower(), 
                                                            self.selected_items,   
                                                            self.get_todays_expenditure(), 
                                                            self.get_todays_calories(), 
                                                            self.order_datetime
                                                            )
        
        
        messagebox.showinfo(title="Order has been placed: ", 
                            message="Your order will be ready in 15 minutes at "+selected_amenity+"\nThank you for your business! ")
        
        
        self.clear_amenity_data()
        self.frame_amenity_order.destroy()
        self.frame_amenity_menu.destroy()

   
       
    def _verify_user_login(self):    
        if not (self.uname.get() and self.upass.get() and self.ucard.get() and self.ufcode.get() ):
            return False
        
        if (self.database.verify_user_login(self.uname.get().lower(), 
                                            self.upass.get(), 
                                            self.ucard.get(), 
                                            self.ufcode.get())):
            print("User {} found in the database".format(self.uname.get()))
            return True
        return False


    def verify_user_funds(self):
        if (self.database.get_user_balance(self.uname.get().lower(), 
                                            self.upass.get(), 
                                            self.ucard.get(), 
                                            self.ufcode.get()
                                            ) >= self.get_todays_expenditure()):
            return True
        return False



    def display_login_info(self, login_frame, wcoords, wfont,fontsize):
        print ( wcoords, wfont,fontsize)
        
        ttk.Label(login_frame, text="Username", 
                  font=(wfont,fontsize)).place(x=wcoords[0][0],y=wcoords[0][1])
                  
        self.username_entry = ttk.Entry(login_frame, 
                                        textvariable=self.uname
                                  ).place(x=wcoords[1][0],y=wcoords[1][1])
        
        ttk.Label(login_frame,text="Password", 
                  font=(wfont,fontsize)).place(x=wcoords[2][0],y=wcoords[2][1])
                  
        self.password_entry = ttk.Entry(login_frame,
                                        textvariable=self.upass, show="*"
                                  ).place(x=wcoords[3][0],y=wcoords[3][1])

        ttk.Label(login_frame, text="Cafecard", 
                  font=(wfont,fontsize)).place(x=wcoords[4][0],y=wcoords[4][1])
        self.usercard_entry = ttk.Entry(login_frame, textvariable=self.ucard
                                  ).place(x=wcoords[5][0],y=wcoords[5][1])
                                  
        ttk.Label(login_frame, text="Family Code",  
                  font=(wfont,fontsize)).place(x=wcoords[6][0],y=wcoords[6][1])
                  
        self.userfcode_entry = ttk.Entry(login_frame, textvariable=self.ufcode
                                  ).place(x=wcoords[7][0],y=wcoords[7][1])
        
        
    def _cancel_the_order(self):
        self.clear_amenity_data()
        self.frame_amenity_order.destroy()
        self.frame_amenity_menu.destroy()



    def _cancel_amenity_menu_selection(self):
        self.clear_amenity_data()
        self.frame_amenity_menu.destroy()


    def clear_amenity_data(self):
        self.upass.set("")
        for self.item_var in self.item_vars:
            self.item_var.set(0)

        self.notebook.tab(0, state='normal')
        self.notebook.tab(1, state='normal')
        self.notebook.tab(2, state='normal')
        
        if self.amenity_type=="CAFE":
            self.cafe_select_button.state(['!disabled'])
            self.cafe_combobox.state(['!disabled'])
            self.cafe_combobox.focus()

        if self.amenity_type=="VendingMachine":
            self.vending_machine_select_button.state(['!disabled'])
            self.vending_machine_combobox.state(['!disabled'])
            self.vending_machine_combobox.focus()
        


#-----------------------------------------------------------
#------------ End of cafe and vending machine order --------
#-----------------------------------------------------------


#-----------------------------------------------------------
#---------------- Beginning of My Account GUI---------------
#-----------------------------------------------------------
           
    def _create_myaccount_GUI(self):
        fc = [(0,0),
              (70,700)]
        wc = [(2,5),
              (73,5),
              (268,5),
              (353,5),
              (2,35),
              (73,35),
              (268,35),
              (353,35)
              ]
        fnt = "Arial Black"
        fsize = 12
        self.frame_myinfo_user_login = ttk.Frame(self.frame_myinfo_login,relief=SUNKEN)
        self.frame_myinfo_user_login.place(x=fc[0][0],y=fc[0][1],height=fc[1][0],width=fc[1][1])
        self.display_login_info(self.frame_myinfo_user_login, wc,fnt,fsize)
        self.login_button = ttk.Button(self.frame_myinfo_user_login, text='Login', command=self._view_profiles)
        self.login_button.place(x=549, y=20)


    def _view_profiles(self):
        if not (self.uname.get() and self.ucard.get() and 
                self.ufcode.get() and self.upass.get()):
            messagebox.showerror("Incomplete Info", "Please enter all info to login")
            return False
          
        if not (self.database.verify_user_login(self.uname.get().lower(), 
                                                self.upass.get(),  
                                                self.ucard.get(), 
                                                self.ufcode.get())):
            messagebox.showerror("User Not Found", "Please Check info and try login again")
            return False
         
        self._display_info()



    def _display_info(self):
        self.frame_welcome_user= ttk.Frame(self.master, relief=SUNKEN)
        self.frame_welcome_user.place(x=0,y=0,height=55,width=700)

        self.frame_myinfo_base=ttk.Frame(self.master,relief = SUNKEN)
        self.frame_myinfo_base.place(x=0,y=55,height=660, width=700)
        
        self.frame_myinfo_logout = ttk.Frame(self.master,relief=SUNKEN)
        self.frame_myinfo_logout.place(x=0,y=661,height=39,width=700)
        
        ttk.Label(self.frame_welcome_user, text="Welcome "+self.uname.get()+"!").place(x=1,y=2)
        ttk.Separator(self.frame_welcome_user).place(x=2,y=20,width=690,height=3)
        
        self.user_balance = self.database.get_user_balance(self.uname.get().lower(), 
                                             self.upass.get(), 
                                             self.ucard.get(), 
                                             self.ufcode.get()
                                             )
        self.user_calories = self.database.get_user_calorie_plan(self.uname.get().lower(), 
                                             self.upass.get(), 
                                             self.ucard.get(), 
                                             self.ufcode.get()
                                             )

        self.dietary_profile_button = ttk.Button(self.frame_welcome_user, text="Display Order History", 
                                                 command=self._display_order_details)
        self.dietary_profile_button.place(x=10,y=25)
        self.expense_profile_button = ttk.Button(self.frame_welcome_user, text="Edit Expense/Calorie plan", 
                                                 command=self._update_balance_calorie_plan)
        self.expense_profile_button.place(x=450,y=25)
        ttk.Button(self.frame_myinfo_logout, text='Logout', 
                   command=self._exit_expense_diet_profile).place(x=310,y=6)

        
    
    def _display_order_details(self):
        self.expense_profile_button.state(['disabled'])
        self.dietary_profile_button.state(['disabled'])
        self.frame_columns_titles_header = ttk.Frame(self.frame_myinfo_base)
        self.frame_columns_titles_header.place(x=0,y=31,height=30,width=700)
        
        self.frame_columns_total_footer = ttk.Frame(self.frame_myinfo_base)
        self.frame_columns_total_footer.place(x=0,y=562,height=30,width=700)

        self.display_current_balance_and_calories_plan()
        
        xposition = 2
        yposition = 2
        ttk.Label(self.frame_columns_titles_header, text='No.   Order_Date').place(x=xposition,y=yposition)
        xposition=xposition + 190
        ttk.Label(self.frame_columns_titles_header, text='Calories').place(x=xposition,y=yposition)
        xposition=xposition + 120
        ttk.Label(self.frame_columns_titles_header, text='Amount_Spent').place(x=xposition,y=yposition)
        xposition=xposition + 145
        ttk.Label(self.frame_columns_titles_header, text='Food_Item_Name').place(x=xposition,y=yposition)
        
        self.frame_orderlistbox = ttk.Frame(self.frame_myinfo_base)
        self.frame_orderlistbox.place(x=1,y=61,height=500,width=698)
        
        self.scrollbar = Scrollbar(self.frame_orderlistbox)
        self.scrollbar.pack( side = RIGHT, fill=Y )
        self.order_listbox = Listbox(self.frame_orderlistbox, yscrollcommand = self.scrollbar.set )
        total_calories = 0
        total_amt_spent= 0
        item_ctr=0
        for order in self.database._get_orders_for_user(self.uname.get().lower(), self.ucard.get(), self.ufcode.get()) :
            item_ctr = item_ctr + 1
            the_str = str(item_ctr)+".  "+"{: <25}".format(order['Order_Date'])+"{:2}".format(' ')+"{: >10n}".format(order['Calories_Consumed'])+"{:25}".format(' ')+"${:>6.2f}".format(order['Amount_Spent'])+"{:30}".format(' ')+"{}".format(order['Food_Item_Name']).ljust(30," ").upper()
            total_calories = total_calories + order['Calories_Consumed']
            total_amt_spent = total_amt_spent + order['Amount_Spent']

            print(the_str)
            self.order_listbox.insert(END, the_str)            
        self.order_listbox.place(x=1,y=0,height=500, width=698)
        self.scrollbar.config( command = self.order_listbox.yview )
        
        xposition = 2
        yposition = 5
        ttk.Label(self.frame_columns_total_footer, text='Total: '+str(item_ctr)).place(x=xposition,y=yposition)
        xposition=xposition + 190
        ttk.Label(self.frame_columns_total_footer, text=str(total_calories)+"Cal").place(x=xposition,y=yposition)
        xposition=xposition + 120
        ttk.Label(self.frame_columns_total_footer, text="$"+str(total_amt_spent)).place(x=xposition,y=yposition)
        
        self.close_order_button = ttk.Button(self.frame_columns_total_footer, text="Close Order Details", command=self._close_order_details)
        self.close_order_button.place(x=500,y=5)



    
    def _update_balance_calorie_plan(self):
        
        self.dietary_profile_button.state(['disabled'])
        self.expense_profile_button.state(['disabled'])
        print("Enter additional amount for the cafe card. and enter no of calories you want to monitor")
        print(self.database.get_user_balance(self.uname.get().lower(), 
                                             self.upass.get(), 
                                             self.ucard.get(), 
                                             self.ufcode.get()
                                             )
              )
        print(self.database.get_user_calorie_plan(self.uname.get().lower(), 
                                             self.upass.get(), 
                                             self.ucard.get(), 
                                             self.ufcode.get()
                                             )
              )

        self.frame_update_profile = ttk.Frame(self.frame_myinfo_base,relief = SUNKEN)
        self.frame_update_profile.place(x=0,y=55,height=100,width=700)
        
        
        self.more_funds = StringVar()
        self.new_calories_plan  = StringVar()

        self.display_current_balance_and_calories_plan()
         
        xposition = 2
        yposition = 20
        ttk.Label(self.frame_update_profile, text='Add More Balance: ').place(x=xposition,y=yposition)
        xposition=xposition + 150
        self.more_balance_entry = ttk.Entry(self.frame_update_profile, textvariable=self.more_funds)
        self.more_balance_entry.place(x=xposition,y=yposition) 
        xposition=xposition + 200

        ttk.Label(self.frame_update_profile, text='Change Calorie Plan:').place(x=xposition,y=yposition)
        xposition=xposition + 150
        self.new_calories_entry = ttk.Entry(self.frame_update_profile, textvariable=self.new_calories_plan)
        self.new_calories_entry.place(x=xposition,y=yposition)
        yposition = yposition +30
        
        
        xposition=200
        self.save_bal_cal_plan_button = ttk.Button(self.frame_update_profile, text="Save", command=self._update_bal_cal)
        self.save_bal_cal_plan_button.place(x=xposition,y=yposition)

        xposition=xposition + 150
        self.exit_bal_cal_plan_button = ttk.Button(self.frame_update_profile, text="Exit", command=self._exit_bal_cal)
        self.exit_bal_cal_plan_button.place(x=xposition,y=yposition)



    def display_current_balance_and_calories_plan(self):
        self.frame_user_info_header = ttk.Frame(self.frame_myinfo_base,relief = SUNKEN)
        self.frame_user_info_header.place(x=0,y=0,height=30,width=700)
        xposition = 2
        yposition = 2
        
        ttk.Label(self.frame_user_info_header, text='User\'s Current Available Balance: ').place(x=xposition,y=yposition)
        xposition=xposition + 230
        self.user_balance_label = ttk.Label(self.frame_user_info_header, text="$"+str(self.user_balance), font=("Arial", 15))
        self.user_balance_label.place(x=xposition,y=yposition)
        
        xposition=xposition + 150

        ttk.Label(self.frame_user_info_header, text='User\'s Current Calorie Plan: ').place(x=xposition,y=yposition)
        xposition=xposition + 190
        self.user_calories_label = ttk.Label(self.frame_user_info_header, text=str(self.user_calories)+"Cal/day" , font=("Arial", 15))
        self.user_calories_label.place(x=xposition,y=yposition)

        
        
    def _update_bal_cal(self):
        
        if self.more_funds.get():
            self.database.add_more_funds_in_usertable(self.uname.get().lower(), 
                                                 self.upass.get(), 
                                                 self.ucard.get(), 
                                                 self.ufcode.get(), 
                                                 self.more_funds.get() )
        if self.new_calories_plan.get():
            self.database.update_diet_plan_in_usertable(self.uname.get().lower(), 
                                                 self.upass.get(), 
                                                 self.ucard.get(), 
                                                 self.ufcode.get(), 
                                                 self.new_calories_plan.get() )
        self.user_balance = self.database.get_user_balance(self.uname.get().lower(), 
                                                 self.upass.get(), 
                                                 self.ucard.get(), 
                                                 self.ufcode.get() )
        self.user_calories = self.database.get_user_calorie_plan(self.uname.get().lower(), 
                                                 self.upass.get(), 
                                                 self.ucard.get(), 
                                                 self.ufcode.get() )
        
        self.frame_user_info_header.destroy()
        self.display_current_balance_and_calories_plan()
        self.more_balance_entry.delete(0, END)
        self.new_calories_entry.delete(0, END)


    def _exit_bal_cal(self):
        self.frame_user_info_header.destroy()
        self.frame_update_profile.destroy()
        self.dietary_profile_button.state(['!disabled'])
        self.expense_profile_button.state(['!disabled'])
        
        
    def _close_order_details(self):
        self.frame_orderlistbox.destroy()
        self.frame_user_info_header.destroy()
        self.frame_columns_titles_header.destroy()
        self.frame_columns_total_footer.destroy()
        self.expense_profile_button.state(['!disabled'])
        self.dietary_profile_button.state(['!disabled'])
        

                    
    def _exit_expense_diet_profile(self):
        self.upass.set("")
        self.frame_welcome_user.destroy()
        self.frame_myinfo_base.destroy()
        self.frame_myinfo_logout.destroy()
    
           
        
        
def main():
    mainCampusWindow = Tk()
#     campusApp = CampusCafeVendingMachineView(mainCampusWindow)
    CampusCafeVendingMachineView(mainCampusWindow)
    mainCampusWindow.mainloop()
    
if __name__ == '__main__':
    main()
    
    
    
    

