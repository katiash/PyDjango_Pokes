#-*- coding: utf-8 -*-
# Python Tuples are Not Just Constant Lists
# () is a tuple: An immutable collection of values, usually (but not necessarily) of different types.
# [] is a list: A mutable collection of values, usually (but not necessarily) of the same type.
# {} is a dict: Use a dictionary for key value pairs.
# For the difference between lists and tuples see here. See also:

from __future__ import unicode_literals
from django.db import models
from datetime import datetime, date
import re
import bcrypt


# USED IN FRIENDS:
# NAME_REGEX = re.compile(r'^([a-zA-Z][a-zA-Z ]+[a-zA-Z])$') #assumes at least 2 strings 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+.[a-zA-Z]+$')
#THESE WILL BE COMBINED TO ALLOW either an EMAIL or USERNAME type of string in USERNAME field:

# EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9]+[a-zA-Z0-9-_]?[a-zA-Z0-9]+@[a-zA-Z]+([a-zA-Z0-9-_]?[a-zA-Z0-9])*?\.+[a-zA-Z]+)$')
# UNAME_REGEX = re.compile(r'^([a-zA-Z]+([0-9]*[-_]?[a-zA-Z0-9]+)*)$')
NAME_REGEX = re.compile(r'^([a-zA-Z]+(\ ?[a-zA-Z]\ ?)*[a-zA-Z]+)$')
#PSWD_REGEX = re.compile(r'^(?=.?\d)(?=.?[A-Z])(?=.?[a-z])(?=.[$@$!%?&])[A-Za-z\d$@$!%?&]{8,}$')

# Create your models here.

#No methods in our new manager should ever catch the whole request object!!! 
# (Just parts, ex. request.POST)
class UserManager(models.Manager):
# unpacking of postData is via a * (i.e. star) if postData is a list, and ** (i.e. kwargs) if
# postData is a dictionary. Ex: def validate_user(self, **postData)
        def validate_user(self, postData):
                response_to_views = {}
                errors = {}
                # errors=[]

                print "****************In UserManager: validate_user method*****************"
                print postData
                print postData['reg_email']
                reg_email = postData['reg_email'].strip(' \t\n\r')
                reg_email = reg_email.lower()
                #Validations example: error["desc"] = "Blog desc should be more than 10 characters" if using error tags.
                name = postData['name'].strip(' \t\n\r')
                print "stripped name: ",name
                print "stripped and lowercased email: ", reg_email
                if not name:
                        # errors.append("Name is required!")
                        errors["name"]="Name is required!"
                elif not NAME_REGEX.match(name):
                        print (NAME_REGEX.match(name))
                        errors["name"]="Your entered Name has either numeric or special characters. \nOnly alphabetic characters and spaces are allowed in the Name field."
                if not postData['alias']:
                        errors["alias"]="Alias is required!"                
                if not reg_email:
                        errors["reg_email"]="Email is absolutely required!"
                elif not EMAIL_REGEX.match(reg_email):
                        errors["reg_email"]="Email format is incorrect. Please re-enter."
                if self.filter(email=reg_email):
                        errors["reg_email"]="There is a already a user registered with this email.\n Might you want to login instead? :)"
                if len(postData['reg_pwd'])<8:
                        errors["reg_pwd"] ="Password must be at least 8 chars long!"
                if len(postData['conf_pwd'])<1:
                        errors["conf_pwd"] = "Please confirm your password!"
                if not postData['reg_pwd'] == postData['conf_pwd']:
                        if errors["conf_pwd"]:
                                errors["conf_pwd"] = errors["conf_pwd"] + "Form passwords must match!"
                        else:
                                errors["conf_pwd"]="Form passwords must match!"
                print postData['dob']
                if not postData['dob']:
                        errors["dob"] ="You have to select a birthdate."
                if not postData['dob'] < unicode(date.today()):
                        errors["dob"] ="You could not possibly be born in the future :D!?"
                #check the errors [] or errors{} for failed validations:
                if errors:
                        response_to_views['status']= False
                        response_to_views['errors']= errors
                        print ("post validations in the if_errors statement, and printing the recorded errors: ", response_to_views['errors'])
                else:
                        response_to_views['status']= True
                        h_reg_pwd = bcrypt.hashpw(postData['reg_pwd'].encode("utf-8"), bcrypt.gensalt())
                        response_to_views['user']=self.create(name=name, alias=postData['alias'], email=reg_email, password=h_reg_pwd, dob=postData['dob'])
                return response_to_views

        def validate_login(self, postData):
                print "************************* in login_validation Manager method*************************"
                print postData
                response_to_views= {} #as a dictionary
                # the .get() method would give us an error if the email does not exist in the User table!
                # so we user .filter(), like " usr = self.filter(email = postData['l_email']) "
                l_email = postData['l_email'].strip(' \t\n\r')
                l_email = l_email.lower()
                u = self.filter(email=l_email)
                # print "Shown object, if found user with this email: ", u  
                
                if u:
                        # print postData['l_pwd']
                        stored_hash = u[0].password
                        # print ("this is the hashed pwd in db: " + stored_hash)
                        if not bcrypt.checkpw(postData['l_pwd'].encode("utf-8"), stored_hash.encode("utf-8")):
                        # could also encrypt same and compare:
                        # input_hash = bcrypt.hashpw(postData['l_pwd'].encode("utf-8"), bcrypt.gensalt())
                        # if not input_hash == stored_hash:
                                response_to_views['status']=False
                                response_to_views['error']="Invalid Password on Login. Please try again."
                        else:
                                response_to_views['status']=True
                                response_to_views['user']=u[0]
                else: #invalid email
                        response_to_views["status"]=False
                        response_to_views['error']="Login E-mail is not recognized. Please re-enter."
                return response_to_views


# Create your models here.
class User(models.Model):
        # Django has pre-built validations, such as specifying a field to
        # be unique. Ex: name = models.CharField(max_length = 255, uniquefield)
        name = models.CharField(max_length=255)
        alias = models.CharField(max_length=255)
        email = models.CharField(max_length=255)
        password = models.CharField(max_length=255)
        dob = models.DateField()
        created_at = models.DateTimeField(auto_now_add = True)
        updated_at = models.DateTimeField(auto_now = True)
        objects = UserManager() # (only needed if you need custom model methods such as validations)
        def __repr__(self):
                return "<User object:   Name: {}, Alias: {}, Email: {}, \n Password: {}, DOB: {}, Created: {}, Updated: {}>".format(self.name, self.alias, self.email, self.password, self.dob, self.created_at, self.updated_at)        

class Poke(models.Model):
        # Django has pre-built validations, such as specifying a field to
        # be unique. Ex: name = models.CharField(max_length = 255, uniquefield)
        created_by = models.ForeignKey(User, related_name = "creator")
        received_by = models.ForeignKey(User, related_name = "receiver")
        created_at = models.DateTimeField(auto_now_add = True)
        updated_at = models.DateTimeField(auto_now = True)