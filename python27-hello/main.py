#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write(u'こんにち123は！')

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
