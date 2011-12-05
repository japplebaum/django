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
        multipart message with auto generated html text
        """
        
        email_msg = shortcuts._render_mail("shortcuts/html.tpl", "person@example.com",
        ["people@example.com"])
        self.assertEqual(email_msg.body, 
            u"This message should be multipart and have an auto generated "+\
    		"plaintext component")

    def test_plain_and_html(self):
        """
        Tests an email with both html and plain
	"""

	email_msg = shortcuts._render_mail("shortcuts/plain_and_html.tpl","person@example.com",
	["people@example.com"])
	self.assertEqual(email_msg.body,
	    u"This is the plaintext block")
	self.assertEqual(email_msg.alternatives,
	    [(u"<span> This is the html block </span>",'text/html')])




    def test_create_message_plaintext(self):

	"""
	Tests if an email is created with plaintext only
	"""

	email_msg = shortcuts._create_message('test_subject', 'test_plain', None,
	"person@example.com", ["people@example.com"], None)

	self.assertEqual(email_msg.body, 'test_plain')
	self.assertEqual(email_msg.attachments, [])


    def test_create_message_html(self):

	"""
	Tests if an email is created in html with specified fields
	"""
	email_msg = shortcuts._create_message('test_subject', None, '<span>test_html</span>',
	"person@example.com", ["people@example.com"], None)

	self.assertEqual(email_msg.body, '')
	self.assertEqual(email_msg.alternatives, [('<span>test_html</span>', 'text/html')])

    def test_create_message_html_and_plain_text(self):

	"""
	Tests if an email is created in html and plaintext with specified fields
	"""
	email_msg = shortcuts._create_message('test_subject', 'test_plain', 'test_html',
	"person@example.com", ["people@example.com"], None)

	self.assertEqual(email_msg.body, 'test_plain')
	self.assertEqual(email_msg.alternatives, [('test_html', 'text/html')])


    
	



