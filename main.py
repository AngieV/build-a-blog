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

# build a blog

import webapp2
import cgi
import jinja2
import os

from google.appengine.ext import db

#set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
class Blog(db.Model):
    title = db.StringProperty(required = True)
    txt_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
class DisplayBlog(Handler):
    def render_blog(self, title="", txt_content="", latest_five=""):
        if not latest_five:
        #display the 5 most recent posts
            latest_five = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
            self.render("display_blog.html", title=title, txt_content=txt_content, latest_five=latest_five)
 
    def get(self):
        self.render_blog()
            
    def post(self):
        self.redirect('/newpost')          
        
class NewPost(Handler):  
    def render_form(self, title="", txt_content="", error=""):
        self.render("newpost_form.html", title=title, txt_content=txt_content, error=error)
        
    def get(self):
        self.render("newpost_form.html")
        
    def post(self):
        #t = jinja_env.get_template("newpost_form.html")
        title = cgi.escape(self.request.get("title"))
        txt_content = (self.request.get("txt_content"))
               
        #if title and body exist, display post on blog
        if title and txt_content:
            #construct a post listing object
            b = Blog(title=title, txt_content = txt_content)
            b.put()
            id = b.key().id()
            self.redirect("/blog/%s" % id)
        else:     
        #display errors appropriately
            error = "Please provide both a title and content."
            self.render_form(title, txt_content, error)
            
class ViewPostHandler(Handler):
    def get(self, id):
        blogpost = Blog.get_by_id(int(id))
        if not blogpost:
            error = "404 Not found: the post you requested does not exist."  
            self.response.write(error)
        else:
            self.response.write(blogpost.title)
            self.response.write(blogpost.txt_content)
            #title = blogpost.title
            #txt_content = blogpost.txt_content
            #self.render("display_blog.html", title=title, txt_content=txt_content)
            
app = webapp2.WSGIApplication([
    ('/blog', DisplayBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
