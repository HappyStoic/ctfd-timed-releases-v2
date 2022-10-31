from CTFd.plugins import register_plugin_assets_directory

from .plugin import plugin_blueprint, process_timed_releases
from .models import TimedReleases


def load(app):
    app.db.create_all()
    app.register_blueprint(plugin_blueprint)

    register_plugin_assets_directory(app, base_path='/plugins/ctfd-timed-releases-v2/src/assets/')

    # wrap existing endpoints that handle challenges to firstly process elapsed timed_releases
    names = [
        "challenges.listing",
        "admin.challenges_detail",
        "admin.challenges_listing",
        "api.challenges_challenge_list"
    ]
    for name in names:
        old_f = app.view_functions[name]
        app.view_functions[name] = wrap_func(old_f, process_timed_releases)


def wrap_func(old_f, wrap_f):
    def wrapper(*args, **kwargs):
        wrap_f()
        return old_f(*args, **kwargs)

    return wrapper
