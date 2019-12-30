"""
WSGI config for IkwenBlog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/home/roddy/PycharmProjects/IkwenBlog/conf')
from conf import monitor

monitor.start(interval=1.0)
monitor.track(os.path.join(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
