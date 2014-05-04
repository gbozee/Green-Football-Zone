from flaskext import wtf
from wtforms.fields.core import SelectMultipleField
from wtforms.ext.appengine.ndb import model_form
from wtforms import validators
from wtforms.fields.simple import TextField, TextAreaField
from wtforms.form import Form

import model
import util

###############################################################################
# Leagues
###############################################################################
class LeagueForm(wtf.Form):
    name = wtf.TextField('Name', [wtf.validators.required()])
    info = wtf.TextField('Info', )
    logo_url = wtf.TextField('Logo Url', [wtf.validators.required()])

    #def __init__(self, *args, **kwargs):
    #    wtf.Form.__init__(self, *args, **kwargs)
    #
    #def validate(self):
    #    rv = wtf.Form.validate(self)
    #    if not rv:
    #        return False
    #    query = model.League.query(model.League.name == self.name.data.lower().title())
    #    league = query.get()
    #    if league:
    #        self.name.errors.append('League already present in database')
    #        return False
    #    else:
    #        return True

###############################################################################
# Teams
###############################################################################
class TeamForm(wtf.Form):
    name = wtf.TextField('Name', [wtf.validators.required()])
    coach = wtf.TextField('Coach Name', )
    administrator = wtf.TextField('Team Administrator', )
    logo_url = wtf.TextField('Logo Url', [wtf.validators.required()])
    info = wtf.TextAreaField('Team Info', )
    #
    #def __init__(self, *args, **kwargs):
    #    wtf.Form.__init__(self, *args, **kwargs)
    #
    #def validate(self):
    #    rv = wtf.Form.validate(self)
    #    if not rv:
    #        return False
    #    query = model.League.query(model.League.name == self.league.data.lower().title())
    #    league = query.get()
    #    if league is None:
    #        self.league.errors.append('League not present in database')
    #        return False
    #    self.league = league
    #    return True

###############################################################################
# Topic
###############################################################################
class TopicForm(wtf.Form):
    title = TextField('Title', [validators.required()])
    body = TextAreaField('Body', [validators.required()])

class ContactUpdateForm(wtf.Form):
    name = wtf.TextField('Name', [wtf.validators.required()])
    email = wtf.TextField('Email', [
        wtf.validators.optional(),
        wtf.validators.email('That does not look like an email'),
    ])
    phone = wtf.TextField('Phone', [wtf.validators.optional()])
    address = wtf.TextAreaField('Address', [wtf.validators.optional()])


class ReplyForm(wtf.Form):
    body = wtf.TextAreaField('Body', [wtf.validators.required()])


class UpdateTopicForm(wtf.Form):
    title = wtf.TextField('Title', [wtf.validators.required()])
