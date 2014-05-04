# -*- coding: utf-8 -*-
from threading import Thread
from google.appengine.api import memcache
import pusher

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import flask

from uuid import uuid4
from datetime import datetime
import time
import urllib
import re
import unicodedata

import config


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

p = pusher.Pusher(app_id='63771',
                  key='7a3da06e97f015d45d27',
                  secret='4e2b107605b3fd2ccb4a')

@async
def create_channel(channel, event='on_load', message=''):
    p[channel].trigger(event, message)



################################################################################
# Request Parameters
################################################################################
def param(name, cast=None):
    '''Returs query parameter by its name, and optionaly casts it to given type.
    Always returns None if the parameter is missing
    '''
    value = None
    if flask.request.json:
        return flask.request.json.get(name, None)

    if value is None:
        value = flask.request.args.get(name, None)
    if value is None and flask.request.form:
        value = flask.request.form.get(name, None)

    if cast and value is not None:
        if cast == bool:
            return value.lower() in ['true', 'yes', '1', '']
        if cast == list:
            return value.split(',') if len(value) > 0 else []
        return cast(value)
    return value


def get_next_url():
    next = param('next')
    if next:
        return next
    referrer = flask.request.referrer
    if referrer and referrer.startswith(flask.request.host_url):
        return referrer
    return flask.url_for('welcome')


################################################################################
# Model manipulations
################################################################################
def retrieve_dbs(query, order=None, limit=None, cursor=None, **filters):
    ''' Retrieves entities from datastore, by applying cursor pagination
    and equality filters. Returns dbs and more cursor value
    '''

    #memcache.set('count',q)
    limit = limit or config.DEFAULT_DB_LIMIT
    cursor = Cursor.from_websafe_string(cursor) if cursor else None
    model_class = ndb.Model._kind_map[query.kind]
    if order:
        for o in order.split(','):
            if o.startswith('-'):
                query = query.order(-model_class._properties[o[1:]])
            else:
                query = query.order(model_class._properties[o])

    for prop in filters:
        if filters.get(prop, None) is None:
            continue
        if isinstance(filters[prop], list):
            for value in filters[prop]:
                query = query.filter(model_class._properties[prop] == value)
        else:
            query = query.filter(model_class._properties[prop] == filters[prop])

    model_dbs, more_cursor, more = query.fetch_page(limit, start_cursor=cursor)
    more_cursor = more_cursor.to_websafe_string() if more else None
    return list(model_dbs), more_cursor

def get_or_set_count_by_memcache(entity_key,query=None,**kwargs):
    entity = memcache.get(entity_key)
    if entity is not None:
        if 'increment' in kwargs:
            if kwargs['increment'] is True:
                memcache.incr(entity_key)
            else:
                memcache.decr(entity_key)
        return entity
    if query:
        q = query.fetch()
        memcache.set(entity_key,len(q))
        return len(q)


def retrieve_dbs2(query,key, limit=None, cursor=None,previous=False, **filters):
    ''' Retrieves entities from datastore, by applying cursor pagination
    and equality filters. Returns dbs and more cursor value
    '''
    is_prev = previous
    q = query
    result = get_or_set_count_by_memcache(key, q)
    limit = limit or config.DEFAULT_DB_LIMIT
    #cursor2 = Cursor.from_websafe_string(cursor) if cursor else None
    cursor2 = Cursor(urlsafe=cursor) if cursor else None
    model_class = ndb.Model._kind_map[query.kind]

    query_forward = query.order(model_class._properties['created'])
    query_reversed = query.order(-model_class._properties['created'])
    if is_prev:
        query = query_reversed
        cursor2 = cursor2.reversed()
    else:
        query = query_forward

    for prop in filters:
        if filters.get(prop, None) is None:
            continue
        if isinstance(filters[prop], list):
            for value in filters[prop]:
                query = query.filter(model_class._properties[prop] == value)
        else:
            query = query.filter(model_class._properties[prop] == filters[prop])

    model_dbs, more_cursor, more = query.fetch_page(limit, start_cursor=cursor2)
    if is_prev:
        prev_cursor = more_cursor.reversed().to_websafe_string() if more else None
        next_cursor = cursor
    else:
        prev_cursor = cursor
        next_cursor = more_cursor.to_websafe_string() if more else None
    return list(model_dbs), next_cursor,prev_cursor,result




################################################################################
# JSON Response Helpers
################################################################################
def jsonify_model_dbs(model_dbs, more_cursor=None):
    '''Return a response of a list of dbs as JSON service result
    '''
    result_objects = []
    for model_db in model_dbs:
        result_objects.append(model_db_to_object(model_db))

    response_object = {
        'status': 'success',
        'count': len(result_objects),
        'now': datetime.utcnow().isoformat(),
        'result': result_objects,
    }
    if more_cursor:
        response_object['more_cursor'] = more_cursor
        response_object['more_url'] = generate_more_url(more_cursor)
    response = jsonpify(response_object)
    return response


def jsonify_model_db(model_db):
    '''Return respons of a db as JSON service result
    '''
    result_object = model_db_to_object(model_db)
    response = jsonpify({
        'status': 'success',
        'now': datetime.utcnow().isoformat(),
        'result': result_object,
    })
    return response


def model_db_to_object(model_db):
    model_db_object = {}
    for prop in model_db._PROPERTIES:
        if prop == 'id':
            try:
                value = json_value(getattr(model_db, 'key', None).id())
            except:
                value = None
        elif prop == 'admin':
            try:
                value = json_value(getattr(model_db, 'key', None).get().username)
            except:
                value = None

        else:
            value = json_value(getattr(model_db, prop, None))
        if value is not None:
            model_db_object[prop] = value
    return model_db_object


def json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
        #return time.mktime(value.timetuple()) * 1000
        #return value
    if isinstance(value, ndb.Key):
        return value.urlsafe()
    if isinstance(value, blobstore.BlobKey):
        return urllib.quote(str(value))
    if isinstance(value, ndb.GeoPt):
        return '%s,%s' % (value.lat, value.lon)
    if isinstance(value, list):
        return [json_value(v) for v in value]
    if isinstance(value, long):
        # Big numbers are sent as strings for accuracy in JavaScript
        if value > 9007199254740992 or value < -9007199254740992:
            return str(value)
    if isinstance(value, ndb.Model):
        return model_db_to_object(value)
    return value


def jsonpify(*args, **kwargs):
    '''Same as flask.jsonify() but returns JSONP if callback is provided
    '''
    if param('callback'):
        content = '%s(%s)' % (param('callback'), flask.jsonify(*args, **kwargs).data)
        mimetype = 'application/javascript'
        return flask.current_app.response_class(content, mimetype=mimetype)
    return flask.jsonify(*args, **kwargs)


################################################################################
# Helpers
################################################################################
def generate_more_url(more_cursor, base_url=None, cursor_name='cursor'):
    '''Substitutes or alters the current request url with a new cursor parameter
    for next page of results
    '''
    if not more_cursor:
        return None
    base_url = base_url or flask.request.base_url
    args = flask.request.args.to_dict()
    args[cursor_name] = more_cursor
    return '%s?%s' % (base_url, urllib.urlencode(args))


def uuid():
    ''' Generates universal unique identifier
    '''
    return uuid4().hex


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


################################################################################
# Lambdas
################################################################################
strip_filter = lambda x: x.strip() if x else ''
