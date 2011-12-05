"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.html import strip_tags
from django import shortcuts
from django.template import Context, loader


class SendTemplatedMailTest(TestCase):
    def test_plaintext_only(self):
        """
        Test that emails created with just a "plain" block are plaintext only
        """
        
        email_msg = shortcuts._render_mail("shortcuts/plain.tpl", 
            "person@example.com",  ["people@example.com"])
        self.assertEqual(email_msg.body, 
            "This message should only have plain text")
        self.assertEqual(email_msg.attachments, [])
    
    def test_html_only(self):
        """
        Test that an email created with only an html block resolves to a
        multipart message with an auto generated
        """
        
        email_msg = shortcuts._render_mail("shortcuts/html.tpl", 
            "person@example.com", ["people@example.com"])
        self.assertEqual(email_msg.body, 
            u"This message should be multipart and have an auto generated "+\
    		"plaintext component")
        self.assertEqual(email_msg.alternatives[0], 
            (u"<span>This message should be multipart and have an auto "+\
                "generated plaintext component</span>", "text/html"))
    def test_plaintext_with_files(self):
        """
        Test that emails with only a "plain" block but with attached files
        are plaintext only but still contain the files within their list of
        attachments
        """
        
        email_msg = shortcuts._render_mail("shortcuts/plain.tpl",
            "person@example.com", ["people@example.com"], files=[__file__])
        self.assertEqual(email_msg.body, 
            "This message should only have plain text")
        self.assertEqual(email_msg.attachments, ["tests.py"])

    def test__create_message_plaintext(self):
        """
        Tests that messages created with only plaintext will have all of the 
        proper fields.
        """
        
        message = shortcuts._create_message("This is a subject", 
            "This is a plaintext message", None, "person@example.com", 
            ["people@example.com"], ["peoplecc@example.com"], 
            ["peoplebcc@example.com"])
        self.assertEqual(message.subject, "This is a subject")
        self.assertEqual(message.body, "This is a plaintext message")
        self.assertEqual(message.from_email, "person@example.com")
        self.assertEqual(message.to, ["people@example.com"])
        self.assertEqual(message.cc, ["peoplecc@example.com"])
        self.assertEqual(message.bcc, ["peoplebcc@example.com"])
        self.assertEqual(message.attachments, [])

    def test__create_message_html(self):
        """
        Tests that messages created with html will have all of the proper fields
        and the body should be empty because _create_message is not responsible
        for creating a plaintext body from an html message. 
        """

        message = shortcuts._create_message("This is a subject", 
            None, u"<span>This is an html message</span>", "person@example.com",
            ["people@example.com"], ["peoplecc@example.com"],     
            ["peoplebcc@example.com"])
        self.assertEqual(message.subject, "This is a subject")
        self.assertEqual(message.body, '')
        self.assertEqual(message.from_email, "person@example.com")
        self.assertEqual(message.to, ["people@example.com"])
        self.assertEqual(message.cc, ["peoplecc@example.com"])
        self.assertEqual(message.bcc, ["peoplebcc@example.com"])
        self.assertEqual(message.attachments, [])
        self.assertEqual(message.alternatives[0], 
           u"<span>This is an html message</span>")
