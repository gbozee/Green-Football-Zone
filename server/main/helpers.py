import urllib

from flask.json import JSONEncoder as BaseJSONEncoder
import datetime
import time
from google.appengine.api import users
from google.appengine.ext import ndb, blobstore
from google.appengine.ext.ndb import query,model
from ndb_json import ModelEncoder



class JSONEncoder(BaseJSONEncoder):
    """Custom :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """
    def default(self, obj):
        # if hasattr(obj, 'to_dict'):
        #     return getattr(obj, 'to_dict')()

        if issubclass(obj.__class__, NDBJsonSerializer):
            return obj.to_json()

        return super(JSONEncoder, self).default(obj)


class NDBJsonSerializer(object):
    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None

    def get_field_names(self):
        for p in self._properties:
            yield p.key

    def to_json(self):

        hidden = self.__json_hidden__ or []

        rv =self.to_dict(exclude=hidden)
        return rv
