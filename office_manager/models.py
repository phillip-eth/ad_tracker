from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
from datetime import datetime, timedelta, timezone, date
import calendar
from django.utils.dateparse import parse_date

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

def num_work_days(month,year):
    thisYear = int(year)
    thisMonth=int(month)
    cal = calendar.Calendar()
    working_days = len([x for x in cal.itermonthdays2(thisYear, thisMonth) if x[0] !=0 and x[1] < 5])
    return (working_days)

class UserManager(models.Manager):
    def reg_validate(self, postData):
        print(postData)
        errors_list=[]
        if len(postData['first_name']) < 2:
            errors_list.append('Your first name must be at least 2 characters long.')
        if len(postData['last_name'])< 2:
            errors_list.append('Your last name must be at least 2 characters long.')
        if not EMAIL_REGEX.match(postData['email']):
            errors_list.append("Please enter a valid email.")
        elif len(User.objects.filter(email = postData['email'])) > 0:
            errors_list.append("That email is already registered.  Please login.")
        if postData['password'] != postData['c_password']:
            errors_list.append("Your passwords do not match.")
        if len(postData['password'])<8:
            errors_list.append("Your password must be at least 8 characters long.")
        if len(errors_list) ==0:
            new_user= self.create(
                f_name = postData['first_name'],
                l_name = postData['last_name'],
                email =  postData['email'],
                role = postData['user_role'],
                password = bcrypt.hashpw(postData['password'].encode("utf-8"), bcrypt.gensalt()),
            )
            
            return (True, new_user)
        else:
            print(errors_list)
            return (False, errors_list)

    def log_validate(self, postData):
        # print('*********',postData)
        errors_list=[]
        user = User.objects.get(email = postData['email'])  
        if user == None:
            errors_list.append("The email / password combo could not be found.  Please try again.")
            return (False , errors_list)
        else: 
            
            u_pw=user.password[2:len(user.password)-1]
            # print(user.password.encode())

        if bcrypt.checkpw(postData['password'].encode(), u_pw.encode()):
            return (True,user)
        else:
            errors_list.append("The email / password combo could not be found.  Please try again.")

        print(errors_list)       
        return (False , errors_list)


class OrderManager(models.Manager):
    def validation(self, postData):
        print(postData)
        appraiser = Appraiser.objects.get(id=postData['appraiser_assigned'])
        client = Client.objects.get(id=postData['client_ordered'])
        product= Product.objects.get(id=postData['product_type'])
        print(appraiser,client,product)
        errors_list=[]
        if len(postData['address']) < 5:
            errors_list.append('The address must be at least 5 characters long.')
        
        if len(postData['fee']) < 2:
            errors_list.append('Please enter a valid fee.')

        if len(postData['due_date'])==0:
            errors_list.append('Please enter a valid due date.')

        if client == False:
            errors_list.append('Please select the client.')

        if appraiser == False:
            errors_list.append('Please assign the appraiser.')

        if product == False:
            errors_list.append('Please enter a valid form type.')

            
        if len(errors_list) == 0:
            if postData['tech_fee'] == "":
                fee_split = float(float(postData['fee'])*appraiser.fee_split_rate)
                t_fee=0
            else:
                fee_split= float(float(postData['fee']) - float(postData['tech_fee']) *appraiser.fee_split_rate)
                t_fee=float(postData['tech_fee'])
            new_order= self.create(
                fee = postData['fee'],
                tech_fee=t_fee,
                app_fee_split=round(fee_split,2),
                address= postData['address'],
                status = 'Add Order',
                due_date = postData['due_date'],
                adding_user =  User.objects.get(id=postData['user_id']),
            )
            print(new_order)
            appraiser.assigned_orders.add(new_order)
            client.orders_placed.add(new_order)
            product.orders_of_type.add(new_order)
            return (True, new_order)
        else:
            print(errors_list)
            return (False, errors_list)

    def filter_by_date_create(self,date):
        return Order.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month,
            created_at__day=date.day
        )

    def filter_by_date_complete(self,date):
        return Order.objects.filter(
            updated_at__year=date.year,
            updated_at__month=date.month,
            updated_at__day=date.day
        )

class ClientManager(models.Manager):
    def validation(self, postData):
        
        errors_list=[]
        if len(Client.objects.filter(name = postData['client_name'])) > 0:
            errors_list.append('That client already exists.')
        if len(postData['client_name']) < 3:
            errors_list.append('The client name must be at least 3 characters long.')
        
        if len(errors_list) == 0:
            
            new_client= self.create(
                name = postData['client_name'],
            )
            return (True, new_client)
        else:
            print(errors_list)
            return (False, errors_list)

class AppraiserManager(models.Manager):
    def validation(self, postData):
        full_name= postData['f_name']+" "+postData['l_name']
        errors_list=[]
        if len(Appraiser.objects.filter(name = full_name)) > 0:
            errors_list.append('That appraiser already exists.')
        if len(full_name) < 3:
            errors_list.append('The appraiser name must be at least 3 characters long.')
        if len(postData['capacity']) ==0 :
            errors_list.append('Please enter the appraiser capacity.')
        if postData['fee_split']=="" :
            errors_list.append('Please enter the appraiser fee split.')
        if postData['license_exp'] == "":
            errors_list.append('Please enter a license expiration date in the future.')
            return (False, errors_list)
        elif parse_date(postData['license_exp']) <= date.today():
            errors_list.append('Please enter a license expiration date in the future.')
        if postData['insurance_exp'] != "" :
            errors_list.append('Please enter an insurance expiration date in the future.')
            return (False, errors_list)
        elif parse_date(postData['insurance_exp']) <= date.today() :
            errors_list.append('Please enter an insurance expiration date in the future.')
        
        if len(errors_list) == 0:
            
            new_appraiser= self.create(
                name = full_name,
                f_name=postData['f_name'],
                l_name= postData['l_name'],
                capacity=postData['capacity'],
                fee_split_rate= float(postData['fee_split']) /100,
                license_exp=postData['license_exp'],
                insurance_exp=postData['insurance_exp'],
            
            )
            return (True, new_appraiser)
        else:
            print(errors_list)
            return (False, errors_list)
    

    def capacity_per_month(self,year,month):
        days = num_work_days(month,year)
        return int(self.capcity * days)

class ProductManager(models.Manager):
    def validation(self, postData):
        
        errors_list=[]
        if len(postData['product_desc']) < 3:
            errors_list.append('The description must be at least 3 characters long.')
        if len(postData['FNMA_form']) < 3:
            errors_list.append('The form # must be at least 3 characters long.')
        if len(errors_list) == 0:
            
            new_prod= self.create(
                desc = postData['product_desc'],
                FNMA_form = postData['FNMA_form']
            )
            return (True, new_prod)
        else:
            print(errors_list)
            return (False, errors_list)

class User(models.Model):
    f_name = models.CharField(max_length=50)
    l_name = models.CharField(max_length = 50)
    email = models.CharField(max_length=255)
    password=models.CharField(max_length = 255)
    role=models.CharField(max_length=15, default="admin")

    objects=UserManager()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.f_name} {self.l_name}" 

    def __repr__(self):
        return f"Show {self.id}, {self.full_name()}"

    my_field_name = models.CharField(max_length=20, help_text='Enter user name')

    class Meta:
        ordering = ['-my_field_name']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        self.my_field_name = self.f_name+" "+self.l_name
        return self.my_field_name

class Appraiser(models.Model):
    name = models.CharField(max_length = 255)
    f_name=models.CharField(max_length = 255, blank=True)
    l_name=models.CharField(max_length = 255, blank=True)
    capacity=models.IntegerField(blank= True, default=2)
    fee_split_rate=models.FloatField(blank=False, default =0.6)
    status = models.CharField(max_length = 15, default="Active")
    license_exp =models.DateTimeField(blank=True, default= datetime.now())
    insurance_exp=models.DateTimeField(blank=True, default= datetime.now())
    insurance_flag=models.BooleanField(default=False)
    license_flag=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    my_field_name = models.CharField(max_length=20, help_text='Enter appraiser name')

    objects=AppraiserManager()

    class Meta:
        ordering = ['-my_field_name']

    def __str__(self):
        self.my_field_name = self.name
        return self.my_field_name

    def display_rate(self):
        return self.fee_split_rate*100

class Client(models.Model):
    name = models.CharField(max_length = 255)
    last_ordered = models.DateTimeField(blank=True, default= datetime.now())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    my_field_name = models.CharField(max_length=20, help_text='Enter client name')

    objects=ClientManager()

    class Meta:
        ordering = ['-my_field_name']

    def __str__(self):
        self.my_field_name = self.name
        return self.my_field_name

class Product(models.Model):
    desc = models.CharField(max_length = 255)
    FNMA_form = models.CharField(max_length = 20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects=ProductManager()

    my_field_name = models.CharField(max_length=40, help_text='Enter product description')

    class Meta:
        ordering = ['-my_field_name']

    def __str__(self):
        self.my_field_name = self.desc
        return self.my_field_name

class Order(models.Model):
    fee= models.FloatField(null=False, blank=True, default=0.0)
    tech_fee= models.FloatField(null=False, blank=True, default=0.0)
    app_fee_split= models.FloatField(null=False, blank=True, default=0.0)
    address= models.CharField(max_length = 255)
    notes= []
    due_date = models.DateTimeField(auto_now=False)
    completed_date =models.DateTimeField(auto_now=False, blank=True, null=True)

    objects=OrderManager()

    Progress_Status= ["Add Order","Assigned","On Hold","Info Requested","Cancelled","Completed"]

    status= models.CharField(max_length=25, blank=False, default = 'Add Order')    


    assigned_appraiser= models.ForeignKey(Appraiser, on_delete=models.SET_NULL, null=True, related_name ="assigned_orders")
    client_ordered= models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name ="orders_placed")
    product_type= models.ForeignKey(Product, on_delete=models.SET_NULL,null=True, related_name ="orders_of_type")
    adding_user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="added_orders")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status','due_date']

    def display(self):
        
        return self.get_status_display()

 
