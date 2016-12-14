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

# create a template directary
template_dir = os.path.join(os.path.dirname(__file__), "templates");

# create an environment instance at the beginning 
# using self-defined loader
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True);

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

class Blog(Handler):
    def get(self):
        self.render("blog.html")

class NewPost(Handler):
	def get(self):
		self.render("newPost.html")
		

app = webapp2.WSGIApplication([
    ('/blog', Blog),
    ('/blog/newpost', NewPost)
], debug=True)
