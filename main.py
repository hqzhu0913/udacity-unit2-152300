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

import os
import webapp2
import jinja2
import re
import hmac
import random

from google.appengine.ext import db

# create a template directary
template_dir = os.path.join(os.path.dirname(__file__), "templates");

# create an environment instance at the beginning 
# using self-defined loader
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir)
	, autoescape = True);

# constant variable
# signup regular expression
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$");
PASSWORD_RE = re.compile(r"^.{3,20}$");
EMAIL_RE = re.compile(r"[\S]+@[\S]+.[\S]+$");
# secret key
SECRET = '';

def valid_username(username):
    return USER_RE.match(username);

def valid_password(password):
	return PASSWORD_RE.match(password);

def valid_email(email):
	return EMAIL_RE.match(email);

def create_hash_value(value):
	hash_value = hmac.new(SECRET, value).hexdigest();
	return "%s|%s" % (value, hash_value);

def check_hash_value(h):
	value = h.split("|")[0]
	if h == create_hash_value(value):
		return value;


class Handler(webapp2.RequestHandler):
	"""
	Handler inherit from webapp2.RequestHandler
	and is parent of MainHandler
	has three functions:
	write, render_str and render
	"""
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw);

	# function takes in filename and a bunch of extra parameters
	# like variable substitution	
	# return a html template string with variable substitution
	def render_str(self, template, **params):
		t = jinja_env.get_template(template);
		return t.render(params);

	# instead of return a string, this function write in the browser
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw));

class Post(db.Model):
	"""
	Post entity(table) has three attributes
	subject is string type
	blog is text type which could have more than 500 characters
	created is the time the entry created. 
	we can order by created desc to show timeline of the posts.
	"""
	subject = db.StringProperty(required = True);
	blog = db.TextProperty(required = True);
	created = db.DateTimeProperty(auto_now_add = True);
	date = db.DateProperty(auto_now_add=True);

class User(db.Model):
	name = db.StringProperty(required = True);
	password = db.StringProperty(required = True);
	email = db.StringProperty();
	
class Blog(Handler):
	"""
	Blog is the page showing at /blog.
	get function define how blog shows
	"""
	def get(self):
		self.render_front();

	def render_front(self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created desc")
		self.render("blog.html", posts=posts)

class NewPost(Handler):
	"""
	new post is the page showing at /blog/newpost
	get function define hwo new post show
	post function define what happen when you submit the form
	"""
	def get(self):
		self.render("newPost.html");

	def post(self):
		subject = self.request.get("subject");
		blog = self.request.get("blog");
		if subject and blog:
			p = Post(subject = subject, blog = blog);
			p.put();
			blog_id = p.key().id();
			self.redirect("/blog/%s" % str(blog_id));
		else:
			error ="Subject and blog, please.";
			self.render("newPost.html", error=error);

class SingleBlog(Handler):
	def get(self, blog_id):
		post = Post.get_by_id(int(blog_id));
		self.render("singleBlog.html", post=post);

class SignUp(Handler):
	def get(self):
		self.render("signup.html");
	def post(self):
		global username;
		# request all the form information
		username = self.request.get('username');
		password = self.request.get('password');
		verify = self.request.get('verify');
		email = self.request.get('email');

		# error message
		usererror = "";
		passworderror = "";
		verifyerror = "";
		emailerror = "";
		error = False;

		if not username or (not valid_username(username)):
			usererror = "That's not a valid username.";
			error = True;
		elif not self.check_name_available(username):
			error = True;
			usererror = "This one is not available. Please try another one."
		if not password or (not valid_password(password)):
			passworderror = "That wasn't a valid password."
			error = True;
		if password != verify:
			verifyerror = "Your passwords didn't match."
			error = True;
		if email and (not valid_email(email)):
			emailerror = "That's not a valid email."
			error = True;
		if error:
			self.render("signup.html"
				, uservalue=username
				, usererror=usererror
				, passworderror=passworderror
				, verifyerror=verifyerror
				, emailerror=emailerror);
		else:
			self.set_cookie("username", username);
			self.set_cookie("password", password);
			if email:
				set_cookie("email", email);
			u = User(name=username, password=password, email=email);
			u.put();
			self.redirect("/blog/welcome?username=" + username);


	def check_name_available(self, name):
		# select all the names from database
		names = db.GqlQuery("SELECT name FROM User");
		for n in names:
			if n == name:
				return False;
		return True;

	def set_cookie(self, name, value):
		cookie_value = create_hash_value(value);
		self.response.headers.add_header('Set-Cookie'
			, "%s=%s; Path=/" % (name, cookie_value))

	def check_cookie():
		name_hash = self.request.cookies.get('username');
		pw_hash = self.request.cookies.get('password');
		username = check_hash_value(name_hash);
		if username and check_hash_value(pw_hash):
			return username;

class Welcome(SignUp):
	"""docstring for Welcome"""
	def get(self):
		username = check_cookie();
		if username:
			self.render("welcome.html", name=username);
		else:
			self.redirect("signup.html");
		

app = webapp2.WSGIApplication([
    (r'/blog', Blog),
    (r'/blog/newpost', NewPost),
    (r'/blog/([0-9]+)', SingleBlog),
    (r'/blog/signup', SignUp),
    (r'/blog/welcome', Welcome)
], debug=True)
