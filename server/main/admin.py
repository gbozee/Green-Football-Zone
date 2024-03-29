# -*- coding: utf-8 -*-

import flask
from flaskext import wtf

import auth
import util
import model
import config

from main import app


class ConfigUpdateForm(wtf.Form):
    analytics_id = wtf.TextField('Analytics ID', filters=[util.strip_filter])
    announcement_html = wtf.TextAreaField('Announcement HTML', filters=[util.strip_filter])
    announcement_type = wtf.SelectField('Announcement Type',
                                        choices=[(t, t.title()) for t in model.Config.announcement_type._choices])
    bitbucket_key = wtf.TextField('Bitbucket Key', filters=[util.strip_filter])
    bitbucket_secret = wtf.TextField('Bitbucket Secret', filters=[util.strip_filter])
    brand_name = wtf.TextField('Brand Name', [wtf.validators.required()], filters=[util.strip_filter])
    dropbox_app_key = wtf.TextField('Dropbox App Key', filters=[util.strip_filter])
    dropbox_app_secret = wtf.TextField('Dropbox App Secret', filters=[util.strip_filter])
    facebook_app_id = wtf.TextField('Facebook App ID', filters=[util.strip_filter])
    facebook_app_secret = wtf.TextField('Facebook App Secret', filters=[util.strip_filter])
    feedback_email = wtf.TextField('Feedback Email', [wtf.validators.optional(), wtf.validators.email()],
                                   filters=[util.strip_filter])
    flask_secret_key = wtf.TextField('Flask Secret Key', [wtf.validators.required()], filters=[util.strip_filter])
    github_client_id = wtf.TextField('GitHub Client ID', filters=[util.strip_filter])
    github_client_secret = wtf.TextField('GitHub Client Secret', filters=[util.strip_filter])
    linkedin_api_key = wtf.TextField('LinkedIn API Key', filters=[util.strip_filter])
    linkedin_secret_key = wtf.TextField('LinkedIn Secret Key', filters=[util.strip_filter])
    twitter_consumer_key = wtf.TextField('Twitter Consumer Key', filters=[util.strip_filter])
    twitter_consumer_secret = wtf.TextField('Twitter Consumer Secret', filters=[util.strip_filter])
    vk_app_id = wtf.TextField('VK App ID', filters=[util.strip_filter])
    vk_app_secret = wtf.TextField('VK App Secret', filters=[util.strip_filter])
    windowslive_client_id = wtf.TextField('Windows Live Client ID', filters=[util.strip_filter])
    windowslive_client_secret = wtf.TextField('Windows Live Client secret', filters=[util.strip_filter])
    google_plus_consumer_id = wtf.TextField('Google Plus Consumer ID', filters=[util.strip_filter])
    google_plus_consumer_secret = wtf.TextField('Google Plus Consumer Secret', filters=[util.strip_filter])


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config_update():
    config_db = model.Config.get_master_db()
    form = ConfigUpdateForm(obj=config_db)
    if form.validate_on_submit():
        form.populate_obj(config_db)
        config_db.put()
        reload(config)
        app.config.update(CONFIG_DB=config_db)
        return flask.redirect(flask.url_for('welcome'))

    if flask.request.path.startswith('/_s/'):
        return util.jsonify_model_db(config_db)

    return flask.render_template(
        'admin/config_update.html',
        title='Admin Config',
        html_class='admin-config',
        form=form,
        config_db=config_db,
        has_json=True,
    )
