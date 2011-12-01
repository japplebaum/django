"""
This module collects helper functions and classes that "span" multiple levels
of MVC. In other words, these functions/classes introduce controlled coupling
for convenience's sake.
"""

from django.template import loader, loader_tags, Context, RequestContext
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.core import urlresolvers, mail
from django.utils.html import strip_tags

def render_to_response(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)

def render(request, *args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    Uses a RequestContext by default.
    """
    httpresponse_kwargs = {
        'content_type': kwargs.pop('content_type', None),
        'status': kwargs.pop('status', None),
    }

    if 'context_instance' in kwargs:
        context_instance = kwargs.pop('context_instance')
        if kwargs.get('current_app', None):
            raise ValueError('If you provide a context_instance you must '
                             'set its current_app before calling render()')
    else:
        current_app = kwargs.pop('current_app', None)
        context_instance = RequestContext(request, current_app=current_app)

    kwargs['context_instance'] = context_instance

    return HttpResponse(loader.render_to_string(*args, **kwargs),
                        **httpresponse_kwargs)

def redirect(to, *args, **kwargs):
    """
    Returns an HttpResponseRedirect to the apropriate URL for the arguments
    passed.

    The arguments could be:

        * A model: the model's `get_absolute_url()` function will be called.

        * A view name, possibly with arguments: `urlresolvers.reverse()` will
          be used to reverse-resolve the name.

        * A URL, which will be used as-is for the redirect location.

    By default issues a temporary redirect; pass permanent=True to issue a
    permanent redirect
    """
    if kwargs.pop('permanent', False):
        redirect_class = HttpResponsePermanentRedirect
    else:
        redirect_class = HttpResponseRedirect

    # If it's a model, use get_absolute_url()
    if hasattr(to, 'get_absolute_url'):
        return redirect_class(to.get_absolute_url())

    # Next try a reverse URL resolution.
    try:
        return redirect_class(urlresolvers.reverse(to, args=args, kwargs=kwargs))
    except urlresolvers.NoReverseMatch:
        # If this is a callable, re-raise.
        if callable(to):
            raise
        # If this doesn't "feel" like a URL, re-raise.
        if '/' not in to and '.' not in to:
            raise

    # Finally, fall back and assume it's a URL
    return redirect_class(to)

def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_404 and get_list_or_404 more DRY.
    """
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, Manager):
        manager = klass
    else:
        manager = klass._default_manager
    return manager.all()

def get_object_or_404(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

def get_list_or_404(klass, *args, **kwargs):
    """
    Uses filter() to return a list of objects, or raise a Http404 exception if
    the list is empty.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    obj_list = list(queryset.filter(*args, **kwargs))
    if not obj_list:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
    return obj_list


def _get_block_node(template, name):
    """
    Get a named BlockNode from a template.
    Returns `None` if a node with the given name does not exist.
    """
    for node in template.nodelist.get_nodes_by_type(loader_tags.BlockNode):
        if node.name == name:
            return node
    return None


def _render_block_node(template, name, context):
    """
    Shortcut to render a named node from a template, using the given context.
    Returns `None` if a node with the given name does not exist.

    Note that leading and trailing whitespace is stripped from the output.
    """
    node = _get_block_node(template, name)
    if node is None:
        return None
    return node.render(context).strip()


def _create_message(subject, plain, html,
                    from_email, recipient_list,
                    cc=None, bcc=None, files=None, **kwargs):
    """
    Return an EmailMessage instance, containing either a plaintext
    representation, or a multipart html/plaintext representation.
    """
    if html:
        message = mail.EmailMultiAlternatives(
            subject or '',
            plain or '',
            from_email,
            recipient_list,
            cc=cc,
            bcc=bcc,
            **kwargs
        )
        message.attach_alternative(html, 'text/html')

    else:
        message = mail.EmailMessage(
            subject or '',
            plain or '',
            from_email,
            recipient_list,
            cc=cc,
            bcc=bcc,
            **kwargs
        )

    for file in files or []:
        message.attach_file(file)

    return message


def _render_mail(template_name, from_email, recipient_list,
                 dictionary=None, context_instance=None,
                 cc=None, bcc=None, files=None, fail_silently=False,
                 html_to_plaintext=strip_tags,
                 **kwargs):
    """
    Returns an EmailMessage instance, rendering the subject and body of the
    email from a template.

    For usage, see `send_templated_mail`.

    Additionally, the following arguments are used:

    `html_to_plaintext` - A function taking a single argument.  If an 'html'
                          block is provided, but a 'plain' block is not, then
                          this function will be used to auto-generate the
                          plaintext of the email body from the html.
                          May be set to `None` to disable this behaviour.
    `**kwargs` - Remaining keyword arguments are passed to the EmailMessage
                 on initialisation. (Eg. 'attachments', 'headers', etc...)
    """
    context_instance = context_instance or Context()
    dictionary = dictionary or {}
    template = loader.get_template(template_name)

    context_instance.update(dictionary)
    try:
        subject = _render_block_node(template, 'subject', context_instance)
        plain = _render_block_node(template, 'plain', context_instance)
        html = _render_block_node(template, 'html', context_instance)
    finally:
        # Revert the context_instance to keep it in the same state.
        context_instance.pop()

    # Always strip newlines from subject.
    if subject:
        subject = ' '.join(subject.splitlines())

    # Auto-generate plaintext portion of the email if required.
    if plain is None and html and html_to_plaintext:
        plain = html_to_plaintext(html)

    message = _create_message(subject, plain, html,
                              from_email, recipient_list, **kwargs)
    return message


def send_templated_mail(template_name, from_email, recipient_list,
                        dictionary=None, context_instance=None,
                        cc=None, bcc=None, files=None, fail_silently=False):
    """
    Sends an email, rendering the subject and body of the email from a
    template.

    The template should contain a block named 'subject', and either/both of a
    'plain' and/or 'html' block.

    * If only the 'plain' block exists, a plaintext email will be returned.
    * If only the 'html' block exists, the plaintext component will be
      automatically generated from the html, and a multipart email will be
      returned.
    * If both the 'plain' and 'html' blocks exist, a multipart email will be
      returned.

    Required arguments:

    `template_name` - The template that should be used to render the email.
    `from_email` - The sender's email address.
    `recipient_list` - A list of reciepient's email addresses.

    Optional arguments:

    `dictionary` - The context dictionary used to render the template.
                   By default, this is an empty dictionary.
    `context_instance` - The Context instance used to render the template.
                         By default, the template will be rendered with a
                         Context instance (filled with values from dictionary).
    `cc` - A list or tuple of recipient addresses used in the "Cc" header when
           sending the email.
    `bcc` - A list or tuple of addresses used in the "Bcc" header when sending
            the email.
    `files` - A list of file paths.  These files will be added as attachments
              on the message.
    ``fail_silently``: A boolean. If it's ``False``, ``send_templated_mail``
                       will raise an ``smtplib.SMTPException`` on failure.
    """
    connection = mail.get_connection()
    message = _render_mail(template_name, from_email, recipient_list,
                           dictionary, context_instance,
                           cc=cc, bcc=bcc, files=files,
                           fail_silently=fail_silently)
    connection.send_messages([message])
