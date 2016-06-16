__author__ = 'deepansh'

from mako.template import Template
from random import randint
from twilio.rest import TwilioRestClient
from datetime import datetime
import cherrypy
import json
import webbrowser


class ContactsApp(object):
    '''

    root URL : displays contacts list from given json string

    '''
    @cherrypy.expose
    def index(self):
        self.__jsonstr = """[
        {"fname":"Deepansh", "lname":"Sachdeva", "mob":"1234567890"},
		{"fname":"Piyush", "lname":"Sharma", "mob":"1234560"},
		{"fname":"Nitin", "lname":"Mehta", "mob":"4567890"},
        {"fname":"Ayush", "lname":"Gupta", "mob":"09765431"}
        ]"""
        data = json.loads(self.__jsonstr)
        mytemplate = Template(filename='ContactList.html')
        return mytemplate.render(data=data)

    '''
    /ContactInfo : displays contacts details using ContactInfo.html template

    @params
    1. fname = first name of contact
    2. lname = last name of contact
    3. mob   = contact number of contact

    '''
    @cherrypy.expose
    def ContactInfo(self, fname=None, lname=None, mob=None):
        contactData = [fname, lname, mob]
        template = Template(filename='ContactInfo.html')
        return template.render(data=contactData)

    '''
    /ComposeMessage : displays text field with OTP generated

    @params
    1. mob = contact number of contact

    '''
    @cherrypy.expose
    def ComposeMessage(self, mob=None):
        otp = randint(100000,999999)
        template = Template(filename='ComposeMessage.html')
        return template.render(data=[otp,mob])

    '''
    /SendMessage : sends sms to contact number using Twillio API

    @params
    1. otp = OTP generated for the contact
    2. mob = mobile number of contact

    '''
    @cherrypy.expose
    def SendMessage(self, otp=None ,mob=None):
        account_sid = "your sid"
        auth_token = "your token"
        client = TwilioRestClient(account_sid, auth_token)
        flag = False

        #check valid mobile number in contact list from json string
        for contact in json.loads(self.__jsonstr):
            if mob == contact["mob"]:
                flag = True
                break
        try:
            if mob != None and mob.isdigit() and len(mob) == 10 and flag:
                message = client.messages.create(to="+91"+mob, from_="+12052824159", body="Hi! Your OTP is "+otp)
                file = open("MessageHistory.txt", "a")
                file.write(mob+","+otp+","+datetime.now().strftime("%H:%M:%S")+"\n")
                file.close()
                return "true"
            else:
                return "false"
        except:
            return "false"
        #return value is obtained in javascript of ComposeMessage.html to display status of send message request from user
    '''
    /MessageHistory : displays OTP sent to contacts with respective time
    '''
    @cherrypy.expose
    def MessageHistory(self):
        historyData = []

        file = open("MessageHistory.txt", "r")
        #read file for OTP sent to mobile number with respective time and create list of dictionaries to render on page
        for row in iter(file):
            rowData = row.strip('\n').split(",")
            rowItem = {"mob":rowData[0], "otp":rowData[1], "time":rowData[2]}
            historyData.append(rowItem)
        historyData.reverse()
        file.close()

        template = Template(filename="SentMessage.html")
        return template.render(data=historyData)


if __name__ == '__main__':
    conf = {
        '/': {
                'tools.sessions.on': True
        }
    }

cherrypy.quickstart(ContactsApp(), '/', conf)
webbrowser.open('http://127.0.0.1:8080')


