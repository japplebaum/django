"""
Unit tests for all of send_templated_mail's helper functions.
"""

from django.test import TestCase
from django.template import Context, loader
from django.utils.html import strip_tags
from django.template.loader_tags import BlockNode
from django import shortcuts


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
        
        