"""
Unit tests for all of send_templated_mail's helper functions.
"""

from django.test import TestCase
from django.template import Context, loader
from django.utils.html import strip_tags
from django.template.loader_tags import BlockNode
from django import shortcuts
from django.template import Context, loader


class SendTemplatedMailTest(TestCase):
    def test_render_mail_plaintext_only(self):
        """
        Test that an email created by _render_node with only a "plain" block is
        plaintext only.
        """
        
        email_msg = shortcuts._render_mail("shortcuts/plain.tpl", 
            "person@example.com",
            ["people@example.com"])
        self.assertEqual(email_msg.body, 
            "This message should only have plain text")
        self.assertEqual(email_msg.attachments, [])
        
                
    def test_render_mail_html_only(self):
        """
        Test that an email created by _render_node with only an html block
        resolves to a multipart message with an auto generated plaintext 
        component.
        """
        
        email_msg = shortcuts._render_mail("shortcuts/html.tpl", 
            "person@example.com",
            ["people@example.com"])
        self.assertEqual(email_msg.body, 
            u"This message should be multipart and have an auto generated "+\
    		"plaintext component")
    	self.assertEqual(email_msg.alternatives[0], 
    	    (u"<span>This message should be multipart and have " +\
    	        "an auto generated plaintext component</span>", 'text/html'))
    	        
    
    def test_render_block_node(self):
        """
        Test that _render_block_node renders the named node if it exists, and
        returns None otherwise.
        """
    
        template = loader.get_template("shortcuts/plain_with_context.tpl")
        context = Context({"word" : " hello "})
        rendered_block = shortcuts._render_block_node(template, "plain", 
            context)
        self.assertEqual(rendered_block, 
            "hello")
        
        empty_block = shortcuts._render_block_node(template, "nonexistent",
            context)
        self.assertEqual(empty_block, None)
        
        
    def test_get_block_node(self):
        """
        Test that _get_block_node gets a named blocknode if it exists and returns
        None otherwise.
        """
        
        template = loader.get_template("shortcuts/plain_and_html.tpl")
        block = shortcuts._get_block_node(template, "plain")
        self.assertEqual(block.name, "plain")
        self.assertEqual(type(block), BlockNode)
        
        
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
           (u"<span>This is an html message</span>", "text/html"))