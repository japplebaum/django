"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.html import strip_tags
from django import shortcuts


class SendTemplatedMailTest(TestCase):
    def test_plaintext_only(self):
        """
        Test that emails created with just a "plain" block are plaintext only
        """
        
        email_msg = shortcuts._render_mail("shortcuts/plain.tpl", "person@example.com",
        ["people@example.com"])
        self.assertEqual(email_msg.body, 
            "This message should only have plain text")
        self.assertEqual(email_msg.attachments, [])
    
    def test_html_only(self):
        """
        Test that an email created with only an html block resolves to a
        multipart message with an auto generated
        """
        
        email_msg = shortcuts._render_mail("shortcuts/html.tpl", "person@example.com",
        ["people@example.com"])
        self.assertEqual(email_msg.body, 
            u"This message should be multipart and have an auto generated "+\
    		"plaintext component")
        