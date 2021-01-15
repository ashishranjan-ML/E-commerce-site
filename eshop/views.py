from django.shortcuts import render
from django.http import HttpResponse
from .models import product, contact, Orders, Orderupdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from paytm import checksum
MERCHANT_KEY = '1234567892323456'
# Create your views here.

def index(request):
    # products = product.objects.all()
    # n = len(products)
    # nSlides = n//4 + ceil((n/4) - (n//4))
    # #params = {'no_of_slides': nSlides, 'range': range(1, nSlides), 'product': products}
    # allprods =[[products, range(1, nSlides), nSlides],
    #           [products, range(1, nSlides), nSlides]]
    allprods=[]
    catprods = product.objects.values('category', 'id')
    cats = {items['category'] for items in catprods}
    for cat in cats:
        prod = product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n//4 + ceil((n/4) - (n//4))
        allprods.append([prod, range(1, nSlides), nSlides])
    params = {'allprods': allprods}
    return render(request, 'eshop/index.html', params)

def searchMatch(query, item):
    query = query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = product.objects.values('category', 'id')
    cats = {items['category'] for items in catprods}
    for cat in cats:
        prodtemp = product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allprods.append([prod, range(1, nSlides), nSlides])
    params = {'allprods': allprods, 'msg': ""}
    if len(allprods) == 0 or len(query) < 3:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'eshop/search.html', params)

def about(request):
    return render(request, 'eshop/about.html')

def cart(request):
    #products = product.objects.filter(id=myid)
    return render(request, 'eshop/cart.html')



def contacts(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        #print(n ame, email, phone, desc)
        contacts = contact(name=name, email=email, phone=phone, desc=desc)
        contacts.save()

    return render(request, 'eshop/contact.html')

def tracker(request):
    if request.method == "POST":
        orderid = request.POST.get('orderid', '')
        email = request.POST.get('email', '')
        #return HttpResponse(f"{orderid} and {email}")
        try:
            order=Orders.objects.filter(order_id=orderid, email=email)
            if len(order) > 0 :
                update = Orderupdate.objects.filter(order_id=orderid)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemjson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')


    return render(request, 'eshop/tracker.html')



def prodView(request, myid):
    products = product.objects.filter(id=myid)
    return render(request, 'eshop/productview.html', {'product': products})

def checkout(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        items_json = request.POST.get('itemsjson', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        order = Orders(name=name, items_json=items_json, email=email, phone=phone, address=address, city=city,
                       state=state, zip_code=zip_code, amount=amount)
        order.save()
        update = Orderupdate(order_id=order.order_id, update_desc="This order has been placed")
        update.save()
        id=order.order_id
        checkthank= True
        #return render(request, 'eshop/checkout.html', {'checkthank': checkthank, 'id': id})
        param_dict = {

            'MID': 'WorldP64425807474247',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'eshop/checkout.html', {'param_dict': param_dict})
    return render(request, 'eshop/checkout.html')

@csrf_exempt
def handlerequest(request):
    #paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] =form[i]
        if i == 'CHECKSUMSASH':
            checksum = form[i]

    verify = checksum.verify_checksum(response_dict,MERCHANT_KEY,checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful beacause' + response_dict['RESPMSG'])

    return render(request, 'eshop/paymentstatus.html', {'response': response_dict})
