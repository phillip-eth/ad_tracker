from re import search
from django.shortcuts import render, redirect
from . models import *
from django.contrib import messages
import datetime
import calendar
from django.utils import timezone
from datetime import date

Progress_Status= ["Add Order","Assigned","On Hold","Info Requested","Cancelled","Completed"]
Months = {
    '01':'Jan',
    '02':'Feb',
    '03':'Mar',
    '04':'Apr',
    '05':'May',
    '06':'Jun',
    '07':'Jul',
    '08':'Aug',
    '09':'Sep',
    '10':'Oct',
    '11':'Nov',
    '12':'Dec',
}
Years = [2021,2022,2023,2024,2025]

def num_work_days(month,year):
    thisYear = int(year)
    thisMonth=int(month)
    cal = calendar.Calendar()
    working_days = len([x for x in cal.itermonthdays2(thisYear, thisMonth) if x[0] !=0 and x[1] < 5])
    return (working_days)


def index(request):
    return render(request,'index.html')

def search_order(request): 
    q=request.POST['search_address']
    if q!="":
        searchResult=Order.objects.filter(address__icontains=q)
        if len(searchResult)>0: 

            print(searchResult)
            context={
                'orders':searchResult,
                'statusList':Progress_Status,
            }
        else:
            context={
                'error': "No orders were located.  Please try again."
            }
        return render(request,'search_results.html',context)
    else:
        context={
                'error': "Please enter a valid search parameter."
            }
        return render(request,'search_results.html',context)

def log_out(request):
    request.session.clear()
    return redirect('/')

def dashboard(request):
    if request.session['user_id'] != None:
        orders= Order.objects.exclude(status="Cancelled").exclude(status="Completed")
        totalFee=0
        totalTechFee=0
        for x in orders:
            totalFee= totalFee+x.fee
            totalTechFee= totalTechFee+x.tech_fee
        subtotalFee=totalFee-totalTechFee
        today=date.today()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        todayOrders=Order.objects.filter_by_date_create(today).exclude(status="Cancelled")
        todayTechFee=0
        todayfee=0
        for o in todayOrders:
            todayfee = todayfee+o.fee
            todayTechFee = todayTechFee+o.tech_fee
        todaySubTotal=todayfee-todayTechFee

        completedOrdersToday=Order.objects.filter_by_date_complete(today).filter(status="Completed")
        completedRevenue=0
        completedTechFee=0
        for i in completedOrdersToday:
            completedRevenue += i.fee
            completedTechFee += i.tech_fee
        compSubTotal=completedRevenue -  completedTechFee

        if totalFee ==0:
            avg_fee = 0
        else:
            avg_fee= round(subtotalFee/len(orders),2)
        context={
            'subtotalFee':round(subtotalFee,2),
            'compSub':round(compSubTotal,2),
            'todaySubTotal':round(todaySubTotal,2),
            'orderCount': len(orders),
            'todayOrder': len(todayOrders),
            'techFees':round(totalTechFee,2),
            'feeAvg':avg_fee,
            'orders':orders,
            'appraiserList':Appraiser.objects.all().order_by('name'),
            'clientList': Client.objects.all().order_by('name'),
            'productList': Product.objects.all().order_by('FNMA_form'),
            'statusList':Progress_Status,
        }
        # print(context['statusList'])
        return render(request,'dashboard.html', context)
    else:
        return redirect('/')

def order_edit(request,pk):
    context={
        'thisOrder':Order.objects.get(id=pk),
        'appraiserList':Appraiser.objects.all(),
        'clientList': Client.objects.all(),
        'productList': Product.objects.all(),
        'statusList':Progress_Status

    }
    return render(request,'order-detail.html', context)

def order_edit_process(request,pk):
    user=User.objects.get(id=request.session['user_id'])
    o=Order.objects.get(id=pk)
    errorslist=[]
    if "address" in request.POST and len(request.POST['address'])>5:
        o.address = request.POST['address']
    else:
        errorslist.append('Please enter a valid address')
    if 'status' in request.POST:
        o.status = request.POST['status']
    if 'due_date' in request.POST:
        if request.POST['due_date'] != "":
            o.due_date = request.POST['due_date']
        else:
            pass
    if 'updated_fee' in request.POST:
        o.fee = request.POST['updated_fee']
    if 'updated_tech_fee' in request.POST:
        o.tech_fee = request.POST['updated_tech_fee']
    if 'assigned_appraiser' in request.POST:
        a=Appraiser.objects.get(id=request.POST['assigned_appraiser'])
        a.assigned_orders.add(o)
    if 'client_ordered' in request.POST:
        c=Client.objects.get(id=request.POST['client_ordered'])
        c.orders_placed.add(o)
    if 'product_type' in request.POST:
        p=Product.objects.get(id=request.POST['product_type'])
        p.orders_of_type.add(o)
    if len(errorslist) > 0:
        for x in range(len(errorslist)):
            print(errorslist[x])
        context={
            'errorslist':errorslist
        }
        return redirect(f"../order_edit/{pk}",context)
    else:
        o.app_fee_split= float(o.fee) - float(o.tech_fee)
        o.save()
        return redirect(f"../order_edit/{pk}")
    

def add_order(request):
    print(request.POST)
    result=Order.objects.validation(request.POST)
    if result[0] == True:
        return redirect("dashboard")
    else:
        for error in result[1]:
            messages.error(request,error)
        return redirect("dashboard")

def update_status(request,pk):
    
    u=str(request.POST['updatedStatus'])
    thisOrder=Order.objects.get(id=pk)
    user=User.objects.get(id=request.session['user_id'])
    if thisOrder.status != u:
        thisOrder.status = request.POST['updatedStatus']
        if u == "Cancelled":
            thisOrder.notes.append(f"The fee for this order was ${thisOrder.fee} before it was cancelled. -by {user.f_name} {user.l_name}, on {date.today()}")
        else:
            thisOrder.notes.append(f"The status has been changed to {request.POST['updatedStatus']} -by {user.f_name} {user.l_name}, on {date.today()}")
        thisOrder.save()
        return redirect('dashboard')
    else:
        return redirect('dashboard')

def delete(request,pk):
    thisOrder=Order.objects.get(id=pk)
    thisOrder.delete()
    return redirect("dashboard")

def complete_order(request,pk):
    o=Order.objects.get(id=pk)
    o.status="Completed"
    o.save()
    return redirect("dashboard")

def sales(request):
    if request.session['user_id'] != None:
        context={
            'months':Months,
            'years':Years,
            'thisMonth': date.today().month,
            'thisYear': date.today().year,
       }
        
        return render(request,'sales_dashboard.html',context)
    else:
        log_out(request)

def run_sales_report(request):
    if request.session['user_id'] != None:

        errorList=[]
        if 'year_selected' in request.POST:
            year=request.POST['year_selected']
        else:
            errorList.append("Please select a valid year.")
        if 'month_selected' in request.POST:
            month=request.POST['month_selected']
        else:
            errorList.append("Please select a valid month.")
        if len(errorList)>0:
            for error in errorList:
                messages.error(request,error)
            return redirect("sales")
        else:
            appraisers=Appraiser.objects.all()
            total_billed=0
            total_tech_fee=0
            month=int(request.POST['month_selected'])
            year=int(request.POST['year_selected'])
            work_days=num_work_days(month,year)
            order_capacity={}
            completed_orders= Order.objects.filter(due_date__month=month).filter(due_date__year=year).filter(status="Completed")
            comp_count= Order.objects.filter(due_date__month=month).filter(due_date__year=year).filter(status="Completed").count()
            count_list={}
            client_list={}
            percent_complete={}
            for j in completed_orders:
                total_billed += j.fee
                total_tech_fee += j.tech_fee
                if j.assigned_appraiser.name in count_list.keys():
                    count_list[j.assigned_appraiser.name] +=1
                else:
                  count_list[j.assigned_appraiser.name] =1

                if j.client_ordered.name in client_list.keys():
                    client_list[j.client_ordered.name] +=1
                else:
                    client_list[j.client_ordered.name] =1
            for a in appraisers:
                order_capacity[a.name]= a.capacity * work_days
                if a.name not in count_list.keys():
                    count_list[a.name]=0
                percent_complete[a.name] =  round((count_list[a.name] / order_capacity[a.name] * 100),2)
            if month < 10:
                st_month=f"0{month}"
            else:
                st_month=str(month)

            for cl in Client.objects.all():
                
                if cl.name in client_list.keys():
                    pass
                else:
                    client_list[cl.name]=0
            if comp_count ==0:
                avg_fee=0
            else:
                avg_fee = round((total_billed-total_tech_fee)/comp_count, 2)
            
            context={
                'completed_orders': Order.objects.filter(due_date__month=month).filter(due_date__year=year).filter(status="Completed"),
                'completed_count':comp_count,
                'appraisers':Appraiser.objects.all(),
                'clients':Client.objects.all(),
                'thisYear':year,
                'thisMonth':Months[st_month],
                'workdays':work_days,
                'count_list':count_list,
                'order_capacity':order_capacity,
                'percent_complete':percent_complete,
                'client_list':client_list,
                'billed':total_billed,
                'tech_fees': total_tech_fee,
                'net_rev': total_billed-total_tech_fee,
                'avg_fee': avg_fee,
            }
            return render(request,'sales_report.html',context)
    else:
        log_out(request)

def run_payroll_report(request):
    if request.session['user_id'] != None:
        errorList=[]
        if 'year_selected' in request.POST:
            year=request.POST['year_selected']
        else:
            errorList.append("Please select a valid year.")
        if 'month_selected' in request.POST:
            month=request.POST['month_selected']
        else:
            errorList.append("Please select a valid month.")
        if len(errorList)>0:
            for error in errorList:
                messages.error(request,error)
            return redirect("sales")
        else:
            appraiser=Appraiser.objects.get(id=request.POST['appraiser_selected'])
            first_billed =0
            second_billed =0
            first_tech =0
            second_tech =0
            month=int(request.POST['month_selected'])
            year=int(request.POST['year_selected'])
            work_days=num_work_days(month,year)
            if month == 1:
                payroll_month = 12
                payroll_year = year-1
            else:
                payroll_month=month-1
                payroll_year=year
            
            print(payroll_month, payroll_year)
            order_capacity=appraiser.capacity * work_days

            completed_orders= Order.objects.filter(due_date__month=payroll_month).filter(due_date__year=payroll_year).filter(status="Completed").filter(assigned_appraiser = appraiser)

            first_period_completed=Order.objects.filter(due_date__month=payroll_month).filter(due_date__year=payroll_year).filter(due_date__day__lt=16).filter(status="Completed").filter(assigned_appraiser = appraiser)

            second_period_completed=Order.objects.filter(due_date__month=payroll_month).filter(due_date__year=payroll_year).filter(due_date__day__gt=15).filter(status="Completed").filter(assigned_appraiser = appraiser)

            count_list=completed_orders.count()
            client_list={}
            percent_complete=round((count_list/ order_capacity * 100),2)
            for j in first_period_completed:
                first_billed += j.app_fee_split
                first_tech += j.tech_fee

                if j.client_ordered.name in client_list.keys():
                    client_list[j.client_ordered.name] +=1
                else:
                    client_list[j.client_ordered.name] =1
            for j in second_period_completed:
                second_billed += j.app_fee_split
                second_tech += j.tech_fee

                if j.client_ordered.name in client_list.keys():
                    client_list[j.client_ordered.name] +=1
                else:
                    client_list[j.client_ordered.name] =1
            if month < 10:
                st_month=f"0{month}"
            else:
                st_month=str(month)

            total_billed=round(first_billed + second_billed,2)
            total_tech_fee=round(first_tech + second_tech,)
            if count_list ==0:
                avg_fee=0
            else:
                avg_fee = round((total_billed-total_tech_fee)/count_list, 2)
           
            context={
                'completed_orders': completed_orders,
                'completed_count':completed_orders.count(),
                'thisYear':year,
                'thisMonth':Months[st_month],
                'workdays':work_days,
                'count_list':count_list,
                'order_capacity':order_capacity,
                'percent_complete':percent_complete,
                'client_list':client_list,
                'billed':total_billed,
                'tech_fees': total_tech_fee,
                'net_rev': total_billed-total_tech_fee,
                'avg_fee': avg_fee,
                'appr':appraiser,
                'first_period':first_period_completed,
                'second_period': second_period_completed,
                'first_billed':round(first_billed,2),
                'first_total_pay':round(first_billed + 375,2),
                'second_billed':round(second_billed,2),
                'second_total_pay':round(second_billed +375,2),
            
            }
            return render(request,'payroll_report.html',context)
    else:
        log_out(request)

def payroll(request):
    if request.session['user_id'] != None:
        context={
            'months':Months,
            'years':Years,
            'thisMonth': date.today().month,
            'thisYear': date.today().year,
            'appraisers':Appraiser.objects.all(),
       }
        
        return render(request,'payroll_dashboard.html',context)
    else:
        log_out(request)


def completed(request):
    if request.session['user_id'] != None:
        context={
            'orders':Order.objects.filter(status="Completed").order_by('-due_date','-updated_at'),
            'statusList':Progress_Status,
            'status':"Completed"
        }
        return render(request,'order-list.html',context)
    else:
        log_out(request)


def order_info_requested(request):
    if request.session['user_id'] != None:
        context={
            'orders':Order.objects.filter(status="Info Requested").order_by('-due_date','-updated_at'),
            'statusList':Progress_Status,
            'status':"Info Requested"
        }
        return render(request,'order-list.html',context)
    else:
        log_out(request)

def cancelled(request):
    if request.session['user_id'] != None:
        context={
            'orders':Order.objects.filter(status="Cancelled").order_by('-due_date','-updated_at'),
            'statusList':Progress_Status,
            'status':"Cancelled"
        }
        return render(request,'order-list.html',context)
    else:
        log_out(request)

def orders_hold(request):
    if request.session['user_id'] != None:
        context={
            'orders':Order.objects.filter(status="On Hold").order_by('-due_date','-updated_at'),
            'statusList':Progress_Status,
            'status':"On Hold"
        }
        return render(request,'order-list.html',context)
    else:
        log_out(request)

def orders_assigned(request):
    if request.session['user_id'] != None:
        context={
            'orders':Order.objects.filter(status="Assigned").order_by('-due_date','-updated_at'),
            'statusList':Progress_Status,
            'status':"Assigned"
        }
        return render(request,'order-list.html',context)
    else:
        log_out(request)

def manage_masters(request):
    if request.session['user_id'] != None:
        context={
            'clients':Client.objects.all().order_by('name'),
            'appraisers':Appraiser.objects.all().order_by('name'),
            'products':Product.objects.all().order_by('FNMA_form'),
        }
        return render(request,'manage.html',context)
    else:
        log_out(request)

def new_client(request):
    print(request.POST)
    result=Client.objects.validation(request.POST)
    if result[0] == True:
        return redirect("manage_masters")
    else:
        for error in result[1]:
            messages.error(request,error)
        return redirect("manage_masters")

def delete_client(request,pk):
    if request.session['user_id'] != None:
        client=Client.objects.get(id=pk)
        client.delete()
        return redirect("manage_masters")
    else:
        log_out(request)

def new_appraiser(request):
    if request.session['user_id'] != None:
        print(request.POST)
        result=Appraiser.objects.validation(request.POST)
        if result[0] == True:
            return redirect("manage_masters")
        else:
            for error in result[1]:
                messages.error(request,error)
            return redirect("manage_masters")
    else:
        log_out(request)

def update_appraiser_capacity(request,pk):
    if request.session['user_id'] != None:
        errorslist=[]
        a=Appraiser.objects.get(id=pk)
        cap= int(request.POST['appraiser_capacity'])
        if cap < 2:
            errorslist.append("The min capacity is 2 per day.")
            for error in errorslist:
                messages.error(request,error)
            return redirect('manage_masters')
        else: 
            a.capacity = cap
            a.save()
            return redirect('manage_masters')      
            
    else:
        log_out(request)


def delete_appraiser(request,pk):
    if request.session['user_id'] != None:
        a=Appraiser.objects.get(id=pk)
        a.delete()
        return redirect("manage_masters")
    else:
        log_out(request)

def new_product(request):
    if request.session['user_id'] != None:
        print(request.POST)
        result=Product.objects.validation(request.POST)
        if result[0] == True:
            return redirect("manage_masters")
        else:
            for error in result[1]:
                messages.error(request,error)
            return redirect("manage_masters")
    else:
        log_out(request)

def delete_product(request,pk):
    if request.session['user_id'] != None:
        a=Product.objects.get(id=pk)
        a.delete()
        return redirect("manage_masters")
    else:
        log_out(request)

def manage_users(request):
    if request.session['user_id'] != None:
        context={
            'users':User.objects.all()
        }
        return render(request,'manage_users.html',context)
    else:
        log_out(request)

def edit_user(request,pk):
    if request.session['user_id'] != None:
        context={
            'user':User.objects.get(id=pk)
        }
        return render(request,'user_detail.html',context)
    else:
        log_out(request)

def process_user_edit(request,pk):
    if request.session['user_id'] != None:
        errors_list=[]
        user = User.objects.get(id = request.POST['userID'])  
        

        if len(request.POST['first_name']) < 2:
            errors_list.append('Your first name must be at least 2 characters long.')
        if len(request.POST['last_name'])< 2:
            errors_list.append('Your last name must be at least 2 characters long.')
        if not EMAIL_REGEX.match(request.POST['email']):
            errors_list.append("Please enter a valid email.")

        if not request.POST['user_role']:
            errors_list.append("Please select the user role.")

        if errors_list==[]:
            user.f_name=str(request.POST['first_name'])
            user.l_name=str(request.POST['last_name'])
            user.email=str(request.POST['email'])
            user.role=str(request.POST['user_role'])
            user.save()
            return redirect('manage_users')
            
        if errors_list !=[]:
            for error in errors_list:
                messages.error(request,error)
            return redirect ('manage_users')
    else:
        log_out(request)

def change_pw(request,pk):
    if request.session['user_id'] != None:
        errors_list=[]
        user = User.objects.get(id = pk) 
        
        if str(request.POST['password']) != str(request.POST['c_password']):
            errors_list.append("Your passwords do not match.")
        if len(request.POST['password'])<8:
            errors_list.append("Your password must be at least 8 characters long.")
    
        if errors_list==[]:
            pw= str(request.POST['password'])
            user.password = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())
            user.save()
            return redirect('manage_users')
            
        if errors_list !=[]:
            for error in errors_list:
                messages.error(request,error)
            return redirect ('manage_users')
    else:
        log_out(request)

def delete_user(request,pk):
    if request.session['user_id'] != None:
        user = User.objects.get(id = pk) 
        user.delete()
        return redirect('manage_users')
    else:
        log_out(request)

def reg_user(request):
    result=User.objects.reg_validate(request.POST)
    
    if result[0] == True:
        
        return redirect('manage_users')
    if result[0]== False:
        for error in result[1]:
            messages.error(request,error)
        return redirect ('manage_users')


def log_user(request):
    result=User.objects.log_validate(request.POST)
    print (result)
    if result[0]== True:
        user=result[1]
        request.session['user_id']=user.id
        request.session['username']=user.f_name
        request.session['user_role']=user.role
        return redirect('dashboard')
    if result[0]== False:
        for error in result[1]:
            messages.error(request,error)
        return redirect ('/')
