DeCart Core
===========

This module contains the core of the DeCart system functionality.

An effort has been made to ensure that the functionality provided here is
modular and reusable regardless of the organisation using DeCart.

In general, the intended use of DeCart as an `app` module is to provide core
templates, models and forms to suit a wide variety of organisational needs. The
`views` for actually generating the site should be written in their own
`project` module at the top level of the repo. From there you can pull in the
pieces of functionality that you require and compose your DeCart system from
existing pieces. Any specialist functionality should be stored in that top level
`project` module, but if you can make it more general, please consider breaking
it out into an additional DeCart module.


## Functionality Provided
- Middleware to ensure that users are always logged in.
- Hierarchical user permissions. (TODO)
- Project overview and evaluation.
- Boundary Partner impact tracking.
- External Partner associations.
- Project funding.
- Forms and AJAX endpoints for live page reload.
- Submission of support queries to the central issue tracker.
