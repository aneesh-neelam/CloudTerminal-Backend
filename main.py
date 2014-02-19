#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, json, datetime, logging
from google.appengine.ext import db


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello from Command Center!')

#Authentication & Binding Classes:
class IDChallenge(webapp2.RequestHandler):
	def get(self):
		q = Users.all()
		count = 0
		for x in q:
			count += 1
		self.response.write(count + 1)

class Authentication(webapp2.RequestHandler):
	def get(self, id, username, password):
		q = Users.all()
		q.filter("username", username)
		newUser = Users(username = str(username), password = str(password), systemID = str(id))
		newUser.put()
		returnValue = []
		returnValue.append(id)
		returnValue.append(username)
		self.response.write(json.dumps(returnValue))

class ClientAuthentication(webapp2.RequestHandler):
	def get(self, username, password):
		q = Users.all()
		q.filter("username", username)
		q.filter("password", password)
		for x in q:
			final = x
		if(final):
			self.response.write(str(final.systemID))
		else:
			self.response.write("AuthenticationError")


#Command Queues:

class CommandAcceptor(webapp2.RequestHandler):
	def get(self,username,commandString):
		if(commandString):
			theUser = Users.all()
			theUser.filter("username", username)
			for x in theUser:
				final = x
			commandObject = Command(command = str(commandString), delivered = False, fromUser = username, toSystemID = final.systemID)
			commandObject.put()
			self.response.write("success")


class CommandDisplayer(webapp2.RequestHandler):
	def get(self, systemID):
		if(systemID):
			commandsForSystemID = Command.all()
			commandsForSystemID.filter("toSystemID", systemID)
			commandsForSystemID.filter("delivered", False)
			commandObjects = []
			logging.info(commandsForSystemID.count())
			#sort according to data later


			for command in commandsForSystemID:
				commandObjects.append(str(command.command))
				command.delivered = True
				command.put()
			logging.info(commandObjects)
			if(len(commandObjects)):
				self.response.write(json.dumps(commandObjects))
			else:
				self.response.write("empty")



class Command(db.Model):
	command = db.StringProperty()
	timestamp = db.DateTimeProperty(auto_now=True)
	delivered = db.BooleanProperty()
	fromUser = db.StringProperty()
	toSystemID = db.StringProperty()
	#exceuted = ...

class Users(db.Model):
	username = db.StringProperty()
	password = db.StringProperty()
	systemID = db.StringProperty()


app = webapp2.WSGIApplication([
    ('/', MainHandler), 
    ('/IDChallenge', IDChallenge), 
    ('/Authentication/(.*)/(.*)/(.*)', Authentication), 
    ('/ClientAuthentication/(.*)/(.*)', ClientAuthentication), 
    ('/CommandAcceptor/(.*)/(.*)', CommandAcceptor), 
    ('/CommandDisplayer/(.*)',CommandDisplayer)
], debug=True)
