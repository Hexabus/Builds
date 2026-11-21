## Timing
- **smollm3**: load 58.2s; 22 answers, avg 19.0s, max 49.7s
- **qwen**: load 103.2s; 22 answers, avg 27.3s, max 42.0s

### what is the default value of CONN_MAX_AGE
**smollm3:** The default value of CONN_MAX_AGE is 0.

Sources:
  [1] ref/settings.txt, 31
  [2] ref/databases.txt, 18
  [3] ref/databases.txt, 2
  [4] ref/databases.txt, 3
_(16.1s)_

**qwen:** The default value of `CONN_MAX_AGE` is `0` [1].

Sources:
  [1] ref/settings.txt, 31
  [2] ref/databases.txt, 18
  [3] ref/databases.txt, 2
  [4] ref/databases.txt, 3
_(25.9s)_

### what is the default value of DATA_UPLOAD_MAX_NUMBER_FIELDS
**smollm3:** The default value of DATA_UPLOAD_MAX_NUMBER_FIELDS is 1000.

Sources:
  [1] ref/settings.txt, 50
  [2] ref/settings.txt, 49
  [3] ref/settings.txt, 205
  [4] releases/1.10.txt, 48
_(14.4s)_

**qwen:** The default value of `DATA_UPLOAD_MAX_NUMBER_FIELDS` is 1000 [1].

Sources:
  [1] ref/settings.txt, 50
  [2] ref/settings.txt, 49
  [3] ref/settings.txt, 205
  [4] releases/1.10.txt, 48
_(26.5s)_

### what is the default value of SESSION_COOKIE_AGE
**smollm3:** The default value of `SESSION_COOKIE_AGE` is 1209600 seconds (2 weeks).

Sources:
  [1] ref/settings.txt, 182
  [2] topics/http/sessions.txt, 16
  [3] topics/http/sessions.txt, 18
  [4] topics/http/sessions.txt, 19
_(18.7s)_

**qwen:** The default value of `SESSION_COOKIE_AGE` is `1209600` (2 weeks, in seconds) [1].

Sources:
  [1] ref/settings.txt, 182
  [2] topics/http/sessions.txt, 16
  [3] topics/http/sessions.txt, 18
  [4] topics/http/sessions.txt, 19
_(35.4s)_

### how long is PASSWORD_RESET_TIMEOUT by default
**smollm3:** The default value for PASSWORD_RESET_TIMEOUT is 259200 seconds, which is equivalent to 3 days. This is mentioned in the passage [2] (releases/3.1.txt, 10).

Sources:
  [1] ref/settings.txt, 174
  [2] releases/3.1.txt, 10
  [3] releases/1.6.txt, 48
  [4] releases/1.6.txt, 50
_(19.4s)_

**qwen:** 259200 seconds (3 days) [1].

Sources:
  [1] ref/settings.txt, 174
  [2] releases/3.1.txt, 10
  [3] releases/1.6.txt, 48
  [4] releases/1.6.txt, 50
_(29.4s)_

### what is the default value of CSRF_COOKIE_NAME
**smollm3:** The default value of CSRF_COOKIE_NAME is 'csrftoken'.

Sources:
  [1] ref/settings.txt, 19
  [2] howto/csrf.txt, 4
  [3] ref/settings.txt, 207
  [4] ref/csrf.txt, 15
_(17.7s)_

**qwen:** The default value of `CSRF_COOKIE_NAME` is `'csrftoken'` [1].

Sources:
  [1] ref/settings.txt, 19
  [2] howto/csrf.txt, 4
  [3] ref/settings.txt, 207
  [4] ref/csrf.txt, 15
_(31.1s)_

### what is the default value of DEFAULT_FROM_EMAIL
**smollm3:** The default value of DEFAULT_FROM_EMAIL is "webmaster@localhost".

Sources:
  [1] ref/templates/api.txt, 44
  [2] ref/settings.txt, 65
  [3] topics/email.txt, 46
  [4] topics/settings.txt, 1
_(15.9s)_

**qwen:** The default value of `DEFAULT_FROM_EMAIL` is `'webmaster@localhost'` [2].

Sources:
  [1] ref/templates/api.txt, 44
  [2] ref/settings.txt, 65
  [3] topics/email.txt, 46
  [4] topics/settings.txt, 1
_(27.5s)_

### what is the default value of the TIME_ZONE setting
**smollm3:** The default value of the TIME_ZONE setting is ``None``. This is mentioned in passages [1] and [2]. Passage [1] states that the default value is ``None`` for the DATABASE-TIME_ZONE setting, and passage [2] states that the default value for the TIME_ZONE setting is ``'America/Chicago'``. However, the question specifically asks about the default value of the TIME_ZONE setting, which is not the same as the DATABASE-TIME_ZONE setting. The default value for the TIME_ZONE setting is ``'America/Chicago'`` as mentioned in passage [2]. But if the question is referring to the DATABASE-TIME_ZONE setting, then the default value is ``None`` as mentioned in passage [1].

Sources:
  [1] ref/settings.txt, 34
  [2] ref/settings.txt, 160
  [3] releases/1.11.txt, 35
  [4] ref/settings.txt, 33
_(27.4s)_

**qwen:** The default value of the `TIME_ZONE` setting is `'America/Chicago'` [2].

Sources:
  [1] ref/settings.txt, 34
  [2] ref/settings.txt, 160
  [3] releases/1.11.txt, 35
  [4] ref/settings.txt, 33
_(25.9s)_

### what is the default value of X_FRAME_OPTIONS
**smollm3:** The default value of X_FRAME_OPTIONS is 'DENY'. This is mentioned in the first passage, which states that by default, the middleware will set the X-Frame-Options header to DENY for every outgoing HttpResponse.

Sources:
  [1] ref/clickjacking.txt, 5
  [2] ref/settings.txt, 171
  [3] ref/settings.txt, 170
  [4] releases/3.0.txt, 19
_(20.7s)_

**qwen:** The default value of `X_FRAME_OPTIONS` is `'DENY'` [1][2][3]. In older versions of Django, the default was `'SAMEORIGIN'` [4].

Sources:
  [1] ref/clickjacking.txt, 5
  [2] ref/settings.txt, 171
  [3] ref/settings.txt, 170
  [4] releases/3.0.txt, 19
_(34.6s)_

### what is the default value of SESSION_ENGINE
**smollm3:** The default value of `SESSION_ENGINE` is ``'django.contrib.sessions.backends.db'``.

Sources:
  [1] ref/settings.txt, 189
  [2] topics/http/sessions.txt, 32
  [3] topics/http/sessions.txt, 8
  [4] topics/http/sessions.txt, 45
_(15.3s)_

**qwen:** The default value of `SESSION_ENGINE` is `'django.contrib.sessions.backends.db'` [1].

Sources:
  [1] ref/settings.txt, 189
  [2] topics/http/sessions.txt, 32
  [3] topics/http/sessions.txt, 8
  [4] topics/http/sessions.txt, 45
_(25.1s)_

### what is the default value of DATA_UPLOAD_MAX_MEMORY_SIZE
**smollm3:** The default value of DATA_UPLOAD_MAX_MEMORY_SIZE is 2621440 bytes (i.e. 2.5 MB). This information is found in passage [2] (ref/settings.txt, 48).

Sources:
  [1] ref/settings.txt, 47
  [2] ref/settings.txt, 48
  [3] ref/settings.txt, 205
  [4] ref/settings.txt, 80
_(17.7s)_

**qwen:** The default value of `DATA_UPLOAD_MAX_MEMORY_SIZE` is `2621440` (i.e. 2.5 MB) [1][2][4].

Sources:
  [1] ref/settings.txt, 47
  [2] ref/settings.txt, 48
  [3] ref/settings.txt, 205
  [4] ref/settings.txt, 80
_(28.5s)_

### what is the default value of FILE_UPLOAD_MAX_MEMORY_SIZE
**smollm3:** The default value of `FILE_UPLOAD_MAX_MEMORY_SIZE` is 2621440 bytes (i.e., 2.5 MB). This information is found in the passage [4] (ref/settings.txt, 202).

Sources:
  [1] ref/settings.txt, 80
  [2] releases/5.2.14.txt, 1
  [3] releases/6.0.5.txt, 1
  [4] ref/settings.txt, 202
_(20.4s)_

**qwen:** The default value of `FILE_UPLOAD_MAX_MEMORY_SIZE` is `2621440` bytes (i.e., 2.5 MB) [1].

Sources:
  [1] ref/settings.txt, 80
  [2] releases/5.2.14.txt, 1
  [3] releases/6.0.5.txt, 1
  [4] ref/settings.txt, 202
_(32.2s)_

### what is the default value of SECURE_HSTS_SECONDS
**smollm3:** The default value of SECURE_HSTS_SECONDS is 0.

Sources:
  [1] ref/settings.txt, 135
  [2] ref/settings.txt, 134
  [3] ref/middleware.txt, 14
  [4] ref/middleware.txt, 12
_(16.4s)_

**qwen:** 0

Sources:
  [1] ref/settings.txt, 135
  [2] ref/settings.txt, 134
  [3] ref/middleware.txt, 14
  [4] ref/middleware.txt, 12
_(25.5s)_

### what is a slug
**smollm3:** A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They're generally used in URLs. For example, in a typical blog entry URL:

https://www.djangoproject.com/weblog/2008/apr/12/spring/

the last bit (spring) is the slug.

Sources:
  [1] glossary.txt, 4
  [2] ref/class-based-views/mixins-single-object.txt, 2
  [3] ref/class-based-views/mixins-single-object.txt, 5
  [4] topics/http/urls.txt, 27
_(22.6s)_

**qwen:** A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They're generally used in URLs [1].

Sources:
  [1] glossary.txt, 4
  [2] ref/class-based-views/mixins-single-object.txt, 2
  [3] ref/class-based-views/mixins-single-object.txt, 5
  [4] topics/http/urls.txt, 27
_(33.1s)_

### what is a view
**smollm3:** A view is a function responsible for rendering a page. It is a part of Django's HTTP request/response framework and is used to handle incoming HTTP requests and return a response to the client. Views can be used to handle various HTTP methods such as GET, POST, PUT, DELETE, etc. They can also be used to render templates, redirect to other URLs, or return custom error messages. In the context of the provided passages, views are discussed in relation to Django's class-based views, including the TemplateView, RedirectView, and other detail views.

Sources:
  [1] glossary.txt, 4
  [2] ref/class-based-views/flattened-index.txt, 2
  [3] ref/class-based-views/flattened-index.txt, 5
  [4] topics/http/views.txt, 10
_(20.4s)_

**qwen:** A view is a function responsible for rendering a page [1].

Sources:
  [1] glossary.txt, 4
  [2] ref/class-based-views/flattened-index.txt, 2
  [3] ref/class-based-views/flattened-index.txt, 5
  [4] topics/http/views.txt, 10
_(25.1s)_

### when was Django 6.1 released
**smollm3:** [1] (releases/index.txt, 1)
=============================
Release notes for the official Django releases. Each release note will tell you
what's new in each version, and will also describe any backwards-incompatible
changes made in that version.

For those :doc:`upgrading to a new version of Django</howto/upgrade-version>`,
you will need to check all the backwards-incompatible changes and
:doc:`deprecated features</internals/deprecation>` for each 'final' release
from the one after your current Django version, up to and including the new
version.

Final releases
==============

Below are release notes through Django |version| and its patch releases. Newer
versions of the documentation contain the release notes for any later releases.

.. _development_release_notes:

6.1 release
-----------
.. toctree::
   :maxdepth: 1

6.1.3
   6.1.2
   6.1.1
   6.1

6.0 release
-----------
.. toctree::
   :maxdepth: 1

[2] (releases/6.1.txt, 1)
========================
Django 6.1 release notes
========================

*August 5, 2026*

Welcome to Django 6.1!

These release notes cover the :ref:`new features <whats-new-6.1>`, as well as
some :ref:`backwards incompatible changes <backwards-incompatible-6.1>` you'll
want to be aware of when upgrading from Django 6.0 or earlier. We've
:ref:`begun the deprecation process for some features
<deprecated-features-6.1>`.

See the :doc:`/howto/upgrade-version` guide if you're updating an existing
project.

Mainstream support is expected to end in April 2027. Extended support is

Sources:
  [1] releases/index.txt, 1
  [2] releases/6.1.txt, 1
  [3] releases/6.1.1.txt, 1
  [4] releases/1.6.1.txt, 4
_(49.7s)_

**qwen:** August 5, 2026 [2]

Sources:
  [1] releases/index.txt, 1
  [2] releases/6.1.txt, 1
  [3] releases/6.1.1.txt, 1
  [4] releases/1.6.1.txt, 4
_(22.9s)_

### which Python versions does Django 6.1 support
**smollm3:** Django 6.1 supports Python 3.12, 3.13, 3.14, and 3.15 (as of 6.1.3).

Sources:
  [1] releases/6.1.txt, 1
  [2] faq/install.txt, 4
  [3] ref/models/querysets.txt, 161
  [4] releases/index.txt, 1
_(22.3s)_

**qwen:** Django 6.1 supports Python 3.12, 3.13, 3.14, and 3.15 [1].

Sources:
  [1] releases/6.1.txt, 1
  [2] faq/install.txt, 4
  [3] ref/models/querysets.txt, 161
  [4] releases/index.txt, 1
_(37.7s)_

### what are the three fetch modes in Django 6.1
**smollm3:** The three fetch modes in Django 6.1 are:

1. FETCH_ONE
2. FETCH_PEERS
3. FETCH_RAISE

These modes control how Django fetches data from the database when an unfetched field is accessed.

Sources:
  [1] topics/db/fetch-modes.txt, 3
  [2] releases/6.1.txt, 3
  [3] topics/db/fetch-modes.txt, 2
  [4] ref/models/instances.txt, 63
_(21.0s)_

**qwen:** The three fetch modes in Django 6.1 are:

1. ``FETCH_ONE``: Fetches the missing field for the current instance only.
2. ``FETCH_PEERS``: Fetches a missing field for all instances that came from the same QuerySet.
3. ``FETCH_RAISE``: Raises a ``FieldFetchBlocked`` exception.

These modes are defined in ``django.db.models.fetch_modes`` and imported into ``django.db.models``.

Sources:
  [1] topics/db/fetch-modes.txt, 3
  [2] releases/6.1.txt, 3
  [3] topics/db/fetch-modes.txt, 2
  [4] ref/models/instances.txt, 63
_(42.0s)_

### what is the default fetch mode
**smollm3:** The default fetch mode is FETCH_ONE. This is mentioned in the first passage, which states that using ``FETCH_RAISE`` for the example would raise an exception at the access of ``book.author``, like:

* 1 query to fetch ``books``
* N queries, where N is the number of books, to fetch the missing ``author`` field

This indicates that the default fetch mode is FETCH_ONE, which fetches the missing field for the current instance only.

Sources:
  [1] topics/db/fetch-modes.txt, 6
  [2] releases/6.1.txt, 3
  [3] topics/db/fetch-modes.txt, 3
  [4] ref/models/instances.txt, 7
_(25.2s)_

**qwen:** FETCH_ONE [2][3]

Sources:
  [1] topics/db/fetch-modes.txt, 6
  [2] releases/6.1.txt, 3
  [3] topics/db/fetch-modes.txt, 3
  [4] ref/models/instances.txt, 7
_(28.0s)_

### what does the FETCH_PEERS fetch mode do
**smollm3:** The FETCH_PEERS fetch mode fetches a missing field for all instances that came from the same initial QuerySet. It works like an on-demand prefetch_related() and can reduce most cases of the "N+1 queries problem" to two queries without any work to maintain a list of fields to prefetch.

Sources:
  [1] releases/6.1.txt, 4
  [2] topics/db/fetch-modes.txt, 5
  [3] topics/db/fetch-modes.txt, 4
  [4] releases/6.1.txt, 3
_(21.0s)_

**qwen:** The `FETCH_PEERS` fetch mode fetches a missing field for all instances that came from the same `QuerySet`. It works like an on-demand `prefetch_related()` and can reduce most cases of the "N+1 queries problem" to two queries [3][4].

Sources:
  [1] releases/6.1.txt, 4
  [2] topics/db/fetch-modes.txt, 5
  [3] topics/db/fetch-modes.txt, 4
  [4] releases/6.1.txt, 3
_(33.2s)_

### when is extended support for Django 6.1 expected to end
**smollm3:** Extended support for Django 6.1 is expected to end in December 2027.

Sources:
  [1] releases/6.1.txt, 1
  [2] releases/6.1.txt, 33
  [3] releases/6.1.txt, 32
  [4] faq/install.txt, 4
_(15.0s)_

**qwen:** December 2027 [1]

Sources:
  [1] releases/6.1.txt, 1
  [2] releases/6.1.txt, 33
  [3] releases/6.1.txt, 32
  [4] faq/install.txt, 4
_(31.6s)_

### how do I configure a Flask blueprint
**smollm3:** Not in my files.
_(0.0s)_

**qwen:** Not in my files.
_(0.0s)_

### what is the recipe for chocolate chip cookies
**smollm3:** Not in my files.
_(0.0s)_

**qwen:** Not in my files.
_(0.0s)_
