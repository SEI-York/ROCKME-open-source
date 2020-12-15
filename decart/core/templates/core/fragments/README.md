Template Fragments
==================

These are page element templates that are compatible with Django's templating
engine, allowing them to be pre-rendered and included within another template as
part of the response from a view.

Each fragment should include some information on what context is expected when
it is rendered and how it should be used in the main template.


### Rendering A Fragment
To render a fragment to HTML do the following:
```python
from django.template.loader import get_template


fragment_template = get_template('core/fragments/my_fragment.html')
context_dict = { ... }  # See individual fragments for their required contexts

html = fragment_template.render(context)
```
You can then pass the resulting HTML to another template as needed.


### A Note On CSRF Tokens
If a template (or any content you are inserting into it) requires access to the
CSRF token you will need to render the template using the following more verbose
syntax in order to inject the request context containing the token.

```python
from django.template.context import RequestContext


html = fragment_template.template.render(
    RequestContext(request, context_dict)
)
```
