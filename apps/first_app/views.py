# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from .models import User, UserManager, Poke
from django.contrib import messages
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db.models import Count
# from checkuser import *

# Create your views here.
def main(request):   
        # @ensure_current_user
        # cannot do (if request.session["user_id"]) because python is unforgiving!
    if "user_id" in request.session:
        print request.session
        request.session.clear()
        return redirect('first_app:pokes')
    else: 
        #context={"my_message" : "Hello, I am your successesful login/registration request"}
        return render(request, 'first_app/main.html')
         
def register(request):
    if request.method=='POST':
        print['****************in view method****************']
        print[request.POST]
        response_from_models = User.objects.validate_user(request.POST)
        print['****************back in view method****************']

        #on successful reg validation
        if response_from_models['status']:
            request.session['user_id']= response_from_models['user'].id
            return redirect('/pokes')   
        #else return redirect ('/')
        else:
            #HOW MESSAGES WORK/PASSED BACK TO CLIENT:
            # The 'messages' object's methods also require the 'request'
            # object to be passed as a first parameter...
            # These messages are then going to be inside of that 'request' 
            # object to pass them back.

            # If errors in response_from_models is not a dictionary, but a list/array:
            # for error in response_from_models['errors']:
            #     messages.error(request, error)            

            # If errors in response_from_models IS a dictionary of tags and error messages:
            for tag, error in response_from_models['errors'].items():
                print tag, error
                messages.error(request, error, extra_tags=tag)
            return redirect('/')    
    else:
        # not a post, redirect to index method?
        return redirect('/') #our main.html template
    
def login(request):
    if request.method=='POST':
        print['****************in view method****************']
        print[request.POST]
        #invoke my method from the User model manager
        response_from_models = User.objects.validate_login(request.POST)
        print "************************* in login view method*************************"
        print response_from_models
        if response_from_models["status"]:
            request.session["user_id"]=response_from_models['user'].id
            #on successful login validation
            return redirect('/pokes')
        else:
            #use the error message to display; will be just one string, so no need to loop through.
            messages.error(request, response_from_models['error'])
            return redirect('/')
    else:
        # not a post, redirect to index method?
        return redirect('first_app:main') #our main.html template


def pokes(request):
    if "user_id" in request.session:
        me=User.objects.filter(id=request.session["user_id"])
        print "I am: ", me[0].name, me[0].id
        all_users = User.objects.all()
        all_but_me = all_users.difference(me)
        my_pokes = Poke.objects.filter(received_by=me[0].id)
        d = {}
        for user in all_but_me:
            count=Poke.objects.filter(received_by=user).count()
            d[user.id]= count
        my_pokes_grouped=my_pokes.values('created_by').annotate(total=Count('created_by')).order_by('total') 
        #print "Trying to group my pokes by user: ", my_pokes_grouped

        context = {
            # 'all_my_plans': all_my_plans,
            # # 'not_friends': not_friends,
            # # 'friends' : friends,
            # 'not_my_plans': not_my_plans,
            'me' : me[0],
            'my_pokes': my_pokes,
            'my_pokes_grouped':my_pokes_grouped,
            'all_but_me': all_but_me,
            'u_dic': d,
            'mystr': "Passed from success views method"
        }
        return render(request, 'first_app/success.html', context)
    else:
        print request.session
        request.session.clear()
        return redirect ('/')

def poke(request, id):
    print "Someone just called the 'poke' method"
    to_poke=get_object_or_404(User, id=id)
    logged_user=User.objects.filter(id=request.session["user_id"])[0]
    poke=Poke.objects.create(created_by=logged_user, received_by=to_poke)
    print "created a poke: ", poke.id
    return redirect('first_app:pokes')

# def join(request, id):
#     print "Someone just called the 'JOIN' method"
#     to_join=get_object_or_404(Plan, id=id)
#     to_friend=User.objects.get(id=id)
#     logged_user=User.objects.get(id=request.session["user_id"])
#     join_result=logged_user.going_on.add(to_join)
#     print join_result
#     return redirect('belt2_app:success')

def logout(request):
    print "Someone just called the 'logout' method "
    #Need to clear that cookie/session dictionary/table =) !
    request.session.clear()
    return redirect('first_app:main')
