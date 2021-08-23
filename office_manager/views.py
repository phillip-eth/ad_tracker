
from re import search
from django.shortcuts import render, redirect
from . models import *
from django.contrib import messages
import datetime
import calendar
from django.utils.timezone import make_aware
from datetime import date, datetime
from django.utils.dateparse import parse_date

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
Years = [2020,2021,2022,2023,2024,2025]

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

            # print(searchResult)
            context={
                'orders':searchResult,
                'statusList':Progress_Status,
                'search_params':q
            }
        else:
            context={
                'error': "No orders were located.  Please try again.",
                'search_params':q
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
        month=datetime.now().month
        year=datetime.now().year
        day=datetime.now().day
        today=datetime.now().today()
        orders= Order.objects.exclude(status="Cancelled").exclude(status="Completed").order_by('status','due_date')
        totalFee=0
        totalTechFee=0
        # count_list={}
        # for app in Appraiser.objects.all().order_by('name'):
        #     if app.name in count_list.keys():
        #         pass
        #     else:
        #         count_list.setdefault(app.name, {})['working']=0
        # for x in orders:
        #     totalFee= totalFee+x.fee
        #     totalTechFee= totalTechFee+x.tech_fee
        #     count_list.setdefault(x.assigned_appraiser.name,{})['working'] +=1
        subtotalFee=totalFee-totalTechFee
        todayOrders=Order.objects.filter_by_date_create(today).exclude(status="Cancelled")
        todayTechFee=0
        todayfee=0
        for o in todayOrders:
            todayfee = todayfee+o.fee
            todayTechFee = todayTechFee+o.tech_fee
        todaySubTotal=todayfee-todayTechFee
        compOrdersThisMonth= Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(status="Completed")
        compRevThisMonth=0
        compTechFeeThisMonth=0
        for j in compOrdersThisMonth:
            compRevThisMonth += j.fee
            compTechFeeThisMonth += j.tech_fee
        completedOrdersToday=Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(completed_date__day=day).filter(status="Completed")
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
        netCombinedRevenue=(compRevThisMonth-compTechFeeThisMonth)+subtotalFee
        context={
            'subtotalFee':round(subtotalFee,2),
            'compSub':round(compSubTotal,2),
            'todaySubTotal':round(todaySubTotal,2),
            'orderCount': len(orders),
            'todayOrder': len(todayOrders),
            'techFees':round(totalTechFee,2),
            'feeAvg':avg_fee,
            'orders':orders,
            'numOrdersCompleted':len(compOrdersThisMonth),
            'combinedRev':netCombinedRevenue,
            'appraiserList':Appraiser.objects.all().filter(status="Active").order_by('name'),
            'clientList': Client.objects.all().order_by('name'),
            'productList': Product.objects.all().order_by('FNMA_form'),
            'statusList':Progress_Status,
            # 'count_list':count_list
        }
        # print(context['statusList'])
        return render(request,'dashboard.html', context)
    else:
        return redirect('/')

def order_edit(request,pk):
    context={
        'thisOrder':Order.objects.get(id=pk),
        'appraiserList':Appraiser.objects.all().filter(status="Active").order_by('name'),
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
        o.app_fee_split= (float(o.fee) - float(o.tech_fee))*o.assigned_appraiser.fee_split_rate
        o.save()
        return redirect(f"../order_edit/{pk}")
    

def add_order(request):
    # print(request.POST)
    result=Order.objects.validation(request.POST)
    if result[0] == True:
        return redirect("dashboard")
    else:
        for error in result[1]:
            messages.error(request,error)
        return redirect("dashboard")


def update_status(request,pk):
    thisOrder=Order.objects.get(id=pk)
    if 'updatedStatus' in request.POST:
        u=str(request.POST['updatedStatus'])
    else:
        u=thisOrder.status
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

def manage_appraisers(request):
    if request.session['user_id'] != None:
        context={
            "appraisers":Appraiser.objects.all()
        }
        return render(request,'manage_appraisers.html',context)

    else:
        log_out(request)

def edit_appraiser(request,pk):
    if request.session['user_id'] != None:
        context={
            'appraiser':Appraiser.objects.get(id=pk),
        }
        return render(request, 'appraiser_detail.html', context)
    else:
        log_out(request)

def process_edit_appraiser(request,pk):
    if request.session['user_id'] != None:
        errorslist=[]
        a=Appraiser.objects.get(id=pk)
        if request.POST['f_name'] != None:
            f_name=request.POST['f_name']
        else: 
            f_name=a.f_name
        if request.POST['l_name'] != None:
            l_name=request.POST['l_name']
        else: 
            l_name=a.f_name
        if float(request.POST['fee_split_rate']) > 65:
            errorslist.append("The max fee split is 65%.")
        elif float(request.POST['fee_split_rate']) < 40:
            errorslist.append("The minimum fee split is 40%")
        if int(request.POST['appraiser_capacity']) < 2:
            errorslist.append("The min capacity is 2 per day.")

        if 'license_exp' in request.POST and request.POST['license_exp'] != "":
            license_e_parse= parse_date(request.POST['license_exp'])
            if license_e_parse <= date.today():
                errorslist.append("The license expiration date must be in the future.")
            else:
                a.license_exp= request.POST['license_exp']

        if 'insurance_exp' in request.POST and request.POST['insurance_exp'] != "":
            insurance_e= parse_date(request.POST['insurance_exp'])
            if insurance_e <= date.today():
                errorslist.append("The insurance expiration date must be in the future.")
            else:
                a.insurance_exp=request.POST['insurance_exp']

        if 'appraiser_status'in request.POST and request.POST["appraiser_status"] != "":
            a.status=request.POST['appraiser_status']

        if len(errorslist)>0:
            for error in errorslist:
                messages.error(request,error)
            return redirect(f'../edit_appraiser/{pk}')
        else: 
            a.f_name=f_name
            a.l_name=l_name
            a.name = f_name+' '+l_name
            a.capacity = int(request.POST['appraiser_capacity'])
            a.fee_split_rate =float(request.POST['fee_split_rate']) / 100
            a.save()
            
            return redirect('manage_appraisers')      
            
    else:
        log_out(request)

def new_appraiser(request):
    if request.session['user_id'] != None:
        # print(request.POST)
        result=Appraiser.objects.validation(request.POST)
        if result[0] == True:
            return redirect("manage_appraisers")
        else:
            for error in result[1]:
                messages.error(request,error)
            return redirect("manage_appraisers")
    else:
        log_out(request)


def delete_appraiser(request,pk):
    if request.session['user_id'] != None:
        a=Appraiser.objects.get(id=pk)
        a.delete()
        return redirect("manage_appraisers")
    else:
        log_out(request)

def complete_order(request,pk):
    o=Order.objects.get(id=pk)
    o.status="Completed"
    o.completed_date=datetime.today()
    o.save()
    return redirect("dashboard")

def sales(request):
    if request.session['user_id'] != None:
        context={
            'months':Months,
            'years':Years,
            'thisMonth': datetime.now().month,
            'thisYear': datetime.now().year,
       }
        
        return render(request,'sales_dashboard.html',context)
    else:
        log_out(request)

def sales_snapshot(request):
    if request.session['user_id'] != None:
        projected_billing=0
        projected_tech_fees=0
        open_rev=0
        open_tech=0
        total_billed=0
        total_tech_fee=0
        month=datetime.now().month
        year=datetime.now().year
        month_total_order= Order.objects.filter(due_date__month=month).filter(due_date__year=year).exclude(status="Cancelled").exclude(status="On Hold")
        work_days=num_work_days(month,year)
        order_capacity={}
        completed_orders= Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(status="Completed")
        working_orders=Order.objects.exclude(status="Completed").exclude(status="Cancelled")
        count_list={}
        client_list={}
        percent_complete={}
        for cl in Client.objects.all().order_by("name"):
            if cl.name in client_list.keys():
                pass
            else:
                client_list.setdefault(cl.name, {})['completed']=0
                client_list.setdefault(cl.name, {})['working']=0
        for app in Appraiser.objects.all().order_by('name'):
            order_capacity[app.name]= app.capacity * work_days
            if app.name in count_list.keys():
                pass
            else:
                count_list.setdefault(app.name, {})['completed']=0
                count_list.setdefault(app.name, {})['working']=0
        for j in completed_orders:
            total_billed += j.fee
            total_tech_fee += j.tech_fee
            count_list.setdefault(j.assigned_appraiser.name,{})['completed'] +=1
            client_list.setdefault(j.client_ordered.name,{})['completed'] +=1
                
        for a in working_orders:
            open_rev += a.fee
            open_tech += a.tech_fee
            count_list.setdefault(a.assigned_appraiser.name,{})['working'] +=1
            client_list.setdefault(a.client_ordered.name,{})['working'] +=1
        for app in Appraiser.objects.all():
            percent_complete[app.name] =  round((count_list[app.name]['completed'] / order_capacity[app.name] * 100),2)
    
        if month < 10:
            st_month=f"0{month}"
        else:
            st_month=str(month)

        if len(completed_orders) ==0 and len(working_orders)==0:
            avg_fee=0
        else:
            avg_fee = ((total_billed+open_rev) -(total_tech_fee+open_tech)) / (len(completed_orders)+len(working_orders))

        for app in month_total_order:
                # print(app)
                projected_billing += app.fee
                projected_tech_fees += app.tech_fee
                
        context={
            'completed_orders': completed_orders,
            'completed_count':len(completed_orders),
            'working_orders': working_orders,
            'working_count':len(working_orders),
            'appraisers':Appraiser.objects.all(),
            'clients':Client.objects.all(),
            'thisYear':year,
            'int_month':int(st_month),
            'thisMonth':Months[st_month],
            'workdays':work_days,
            'count_list':count_list,
            'order_capacity':order_capacity,
            'percent_complete':percent_complete,
            'client_list':client_list,
            'billed':total_billed-total_tech_fee,
            'tech_fees': round(total_tech_fee+open_tech,2),
            'net_rev': (total_billed-total_tech_fee)+(open_rev-open_tech),
            'working_rev':open_rev-open_tech,
            'avg_fee': round(avg_fee,2),
            'monthly_billing': (total_billed+projected_billing)-(total_tech_fee+projected_tech_fees),
        }
        return render(request,'sales_snapshot.html',context)
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
            appraisers=Appraiser.objects.filter(status="Active")
            total_billed=0
            total_tech_fee=0
            month=int(request.POST['month_selected'])
            year=int(request.POST['year_selected'])
            work_days=num_work_days(month,year)
            order_capacity={}
            completed_orders= Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(status="Completed")
            comp_count= Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(status="Completed").count()
            count_list={}
            count_list["Deleted Appraiser"]=0
            client_list={}
            percent_complete={}
            for j in completed_orders:
                total_billed += j.fee
                total_tech_fee += j.tech_fee
                if j.assigned_appraiser == None:
                    count_list['Deleted Appraiser'] +=1

                elif j.assigned_appraiser.name in count_list.keys():
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
                'completed_orders': completed_orders,
                'completed_count':comp_count,
                'appraisers':Appraiser.objects.all(),
                'clients':Client.objects.all(),
                'thisYear':year,
                'int_month':int(st_month),
                'thisMonth':Months[st_month],
                'workdays':work_days,
                'count_list':count_list,
                'order_capacity':order_capacity,
                'percent_complete':percent_complete,
                'client_list':client_list,
                'billed':total_billed,
                'tech_fees': round(total_tech_fee,2),
                'net_rev': total_billed-total_tech_fee,
                'avg_fee': avg_fee,
                
            }
            return render(request,'sales_report.html',context)
    else:
        log_out(request)

def sales_by_client(request,name,mnth,yr):
    if request.session['user_id'] != None:
        client=Client.objects.get(name=name)
        total_billed=0
        total_tech_fee=0
        month=mnth
        year=yr
        work_days=num_work_days(month,year)
        completed_orders= Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(status="Completed").filter(client_ordered=client)
        comp_count= len(completed_orders)
        appraiser_list={}
        for j in completed_orders:
            total_billed += j.fee
            total_tech_fee += j.tech_fee
            if j.assigned_appraiser.name in appraiser_list.keys():
                appraiser_list[j.assigned_appraiser.name] +=1
            else:
                appraiser_list[j.assigned_appraiser.name] =1
        
        if month < 10:
            st_month=f"0{month}"
        else:
            st_month=str(month)
        for appr in Appraiser.objects.all():
            if appr.name in appraiser_list.keys():
                pass
            else:
                appraiser_list[appr.name]=0
        if comp_count ==0:
            avg_fee=0
        else:
            avg_fee = round((total_billed-total_tech_fee)/comp_count, 2)
        context={
            'completed_orders': completed_orders,
            'completed_count':comp_count,
            'appraisers':appraiser_list,
            'client':client,
            'thisYear':year,
            'int_month':int(st_month),
            'thisMonth':Months[st_month],
            'workdays':work_days,
            'billed':total_billed,
            'tech_fees': total_tech_fee,
            'net_rev': total_billed-total_tech_fee,
            'avg_fee': avg_fee,
        }
        return render(request,'client_sales_report.html',context)
    else:
        log_out(request)

def sales_by_appraiser(request,pk,mnth,yr):
    if request.session['user_id'] != None:

        appraiser=Appraiser.objects.get(id=pk)
        total_billed=0
        total_tech_fee=0
        month=mnth
        year=yr
        work_days=num_work_days(month,year)
        completed_orders= Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(status="Completed").filter(assigned_appraiser=appraiser)
        comp_count= len(completed_orders)
        client_list={}
        for j in completed_orders:
            total_billed += j.fee
            total_tech_fee += j.tech_fee
            if j.client_ordered.name in client_list.keys():
                client_list[j.client_ordered.name] +=1
            else:
                client_list[j.client_ordered.name] =1
        
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
            'completed_orders': completed_orders,
            'completed_count':comp_count,
            'appraiser':appraiser,
            'clients':Client.objects.all(),
            'thisYear':year,
            'int_month':int(st_month),
            'thisMonth':Months[st_month],
            'workdays':work_days,
            'order_capacity':appraiser.capacity * work_days,
            'percent_complete':round((comp_count / (appraiser.capacity * work_days) * 100),2),
            'client_list':client_list,
            'billed':total_billed,
            'tech_fees': total_tech_fee,
            'net_rev': total_billed-total_tech_fee,
            'avg_fee': avg_fee,
            
        }
        return render(request,'appraiser_sales_report.html',context)
    else:
        log_out(request)

def recap_today(request):
    if request.session['user_id'] != None:
        month=datetime.now().month
        year=datetime.now().year  
        day=datetime.now().day
        new_order_rev=0
        today_tech_fee=0
        today_billed=0
        completed_tech=0
        today_q = datetime.now().today()
        completed_orders=  Order.objects.filter(completed_date__month=month).filter(completed_date__year=year).filter(completed_date__day=day).filter(status="Completed")
        new_order_list=Order.objects.filter_by_date_create(today_q).exclude(status="Cancelled")
        appraiser_list={}
        client_list={}
        company_split=0

        for app in Appraiser.objects.all().order_by('name'):
            if app.name in appraiser_list.keys():
                pass
            else:
                appraiser_list.setdefault(app.name, {})['completed']=0
                appraiser_list.setdefault(app.name, {})['new_orders']=0
                appraiser_list.setdefault(app.name, {})['new_rev']=0
                appraiser_list.setdefault(app.name, {})['billed_rev']=0
                appraiser_list.setdefault(app.name, {})['capacity']=app.capacity

        for order in new_order_list:
            if order.client_ordered.name in client_list.keys():
                pass
            else:
                client_list.setdefault(order.client_ordered.name, {})['new_orders']=0
                client_list.setdefault(order.client_ordered.name, {})['new_rev']=0
            

            client_list.setdefault(order.client_ordered.name, {})['new_orders']+=1
            client_list.setdefault(order.client_ordered.name, {})['new_rev']+=order.fee
            appraiser_list.setdefault(order.assigned_appraiser.name, {})['new_orders']+=1
            appraiser_list.setdefault(order.assigned_appraiser.name, {})['new_rev']+=order.fee
            new_order_rev += order.fee
            today_tech_fee += order.tech_fee
            company_split += (order.fee-order.app_fee_split)
                
        for o  in completed_orders:
            if o.client_ordered.name in client_list.keys():
                if 'completed' in client_list[o.client_ordered.name].keys():
                    pass
                else:
                    client_list.setdefault(o.client_ordered.name, {})['completed']=0

                if 'billed_rev' in client_list[o.client_ordered.name].keys():
                    pass
                else:
                    client_list.setdefault(o.client_ordered.name, {})['billed_rev']=0    
                
            else:
                client_list.setdefault(o.client_ordered.name, {})['completed']=0
                client_list.setdefault(o.client_ordered.name, {})['billed_rev']=0

            if o.assigned_appraiser.name in appraiser_list.keys():
                pass
            else:
                appraiser_list.setdefault(o.assigned_appraiser.name, {})['completed']=0
                appraiser_list.setdefault(o.assigned_appraiser.name, {})['billed_rev']=0
                appraiser_list.setdefault(o.assigned_appraiser.name, {})['new_rev']=0
                appraiser_list.setdefault(o.assigned_appraiser.name, {})['billed_rev']=0
                appraiser_list.setdefault(o.assigned_appraiser.name, {})['capacity']=0
            
            client_list.setdefault(o.client_ordered.name, {})['completed']+=1
            client_list.setdefault(o.client_ordered.name, {})['billed_rev']+=o.fee
            appraiser_list.setdefault(o.assigned_appraiser.name, {})['completed']+=1
            appraiser_list.setdefault(o.assigned_appraiser.name, {})['billed_rev']+=o.fee
            completed_tech+= o.tech_fee
            today_billed+= o.fee
            company_split += (o.fee-o.app_fee_split)
       
        if len(completed_orders) ==0:
            completed_avg_fee=0
        else:
            completed_avg_fee = round((today_billed-completed_tech)/len(completed_orders),2)

        if len(new_order_list) ==0:
            new_avg_fee=0
        else:
            new_avg_fee = round((new_order_rev-today_tech_fee)/len(new_order_list),2)
        
        context={
            'completed_orders': completed_orders,
            'completed_count':len(completed_orders),
            'new_orders': new_order_list,
            'new_count':len(new_order_list),
            'appraisers':Appraiser.objects.all().order_by('name'),
            'clients':Client.objects.all(),
            'client_list':client_list,
            'appraiser_list':appraiser_list,
            'billed':today_billed,
            'billed_tech_fees': completed_tech,
            'net_billed_rev': today_billed-completed_tech,
            'new_rev': new_order_rev,
            'new_tech_fees':today_tech_fee,
            'new_net_rev': new_order_rev-today_tech_fee,
            'completed_avg_fee': completed_avg_fee,
            'new_avg_fee': new_avg_fee,
            'company_split':round(((today_billed-completed_tech)*0.4),2),
            'today':today_q,
        }
        return render(request,'recap_today.html',context)
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
            feeTotal=0
            first_tech =0
            month=int(request.POST['month_selected'])
            year=int(request.POST['year_selected'])
            work_days=num_work_days(month,year)
            if month == 1:
                payroll_month = 12
                payroll_year = year-1
            else:
                payroll_month=month-1
                payroll_year=year
            
            # print(payroll_month, payroll_year)
            order_capacity=appraiser.capacity * work_days

            # completed_orders= Order.objects.filter(due_date__month=payroll_month).filter(due_date__year=payroll_year).filter(status="Completed").filter(assigned_appraiser = appraiser)

            if month < 10:
                st_month=f"0{month}"
            else:
                st_month=str(month)
            if request.POST['payroll_period'] == '1':
                pay_period = f"1st of {Months[st_month]}, {payroll_year}"
                period_completed=Order.objects.filter(completed_date__month=payroll_month).filter(completed_date__year=payroll_year).filter(completed_date__day__lt=16).filter(status="Completed").filter(assigned_appraiser = appraiser)
            else:
                pay_period = f"15th of {Months[st_month]}, {payroll_year}"
                period_completed=Order.objects.filter(completed_date__month=payroll_month).filter(completed_date__year=payroll_year).filter(completed_date__day__gt=15).filter(status="Completed").filter(assigned_appraiser = appraiser)

            count_list=period_completed.count()
            client_list={}
            percent_complete=round((count_list/ order_capacity * 100),2)
            for j in period_completed: 
                first_billed += (j.fee - j.tech_fee)
                first_tech += j.tech_fee
                feeTotal += j.fee
                j.fee_split_rate = (j.fee - j.tech_fee) * appraiser.fee_split_rate
                j.save()

                if j.client_ordered.name in client_list.keys():
                    client_list[j.client_ordered.name] +=1
                else:
                    client_list[j.client_ordered.name] =1
            

            total_billed=round(first_billed * appraiser.fee_split_rate,2)
            total_tech_fee=round(first_tech)
            if count_list ==0:
                avg_fee=0
            else:
                avg_fee = round(feeTotal/count_list, 2)
           
            context={
                'completed_count':count_list,
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
                'appr_fee_split_rate':appraiser.fee_split_rate,
                'pay_period_completed':period_completed,
                'first_total_pay':round(total_billed + 375,2),
                'fee_split_rate':appraiser.fee_split_rate *100,
                'pay_period':pay_period
            
            }
            return render(request,'payroll_report.html',context)
    else:
        log_out(request)

def payroll(request):
    if request.session['user_id'] != None:
        context={
            'months':Months,
            'years':Years,
            'thisMonth': datetime.now().month,
            'thisYear': datetime.now().year,
            'appraisers':Appraiser.objects.all(),
       }
        
        return render(request,'payroll_dashboard.html',context)
    else:
        log_out(request)


def completed(request):
    if request.session['user_id'] != None:
        context={
            'orders':Order.objects.filter(status="Completed").order_by('-completed_date','due_date'),
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
        return render(request,'manage_masters.html',context)
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

