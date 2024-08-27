import os
import datetime
import dateutil.parser
from dateutil.utils import default_tzinfo

from CTFd.models import Challenges, db
from CTFd.utils.decorators import admins_only

from flask import Blueprint, render_template_string, request, jsonify, redirect
from .models import TimedReleases

plugin_blueprint = Blueprint("timed_releases", __name__)


@plugin_blueprint.route("/admin/timed_releases", methods=["GET"])
@admins_only
def timed_releases():
    process_timed_releases()

    chals = Challenges.query.order_by(Challenges.id).all()

    times = TimedReleases.query.order_by(TimedReleases.id).all()
    challenge_to_time = {t.chalid: t.release for t in times}

    res = []
    for c in chals:
       res.append({
           "id": c.id,
           "name": c.name,
           "state": c.state,
           "timed_release": challenge_to_time.get(c.id, "—")
       })

    template = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets/index.html'))
    with open(template, 'r') as t:
        content = t.read()
    return render_template_string(content, challenges=res)


@plugin_blueprint.route("/admin/timed_releases/<chal_id>", methods=["POST"])
@admins_only
def update_timed_release(chal_id):
    # check challenge exists
    Challenges.query.filter_by(id=chal_id).first_or_404()

    release_time = request.form.get("release")
    try:
        # convert string of the form 2018-06-12T19:30 to a datetime
        release_time = default_tzinfo(dateutil.parser.parse(release_time), datetime.timezone.utc)
    except ValueError:
        return jsonify({"error": "invalid date format"}), 400

    chal = Challenges.query.filter_by(id=chal_id).first_or_404()

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    if release_time < utc_now:
        return jsonify({"error": "provided date is in the past"}), 400

    # update existing timed release or create a new one
    tr = db.session.query(TimedReleases).filter(TimedReleases.chalid == chal_id).first()
    if tr is None:
        db.session.add(TimedReleases(chalid=chal.id, release=release_time))
    else:
        tr.release = release_time

    db.session.commit()
    db.session.close()
    return jsonify({"msg": "ok"})


@plugin_blueprint.route("/admin/timed_releases/delete/<chal_id>", methods=["GET"])
@admins_only
def delete_timed_release(chal_id):
    timed_release = TimedReleases.query.filter_by(chalid=chal_id).first_or_404()
    db.session.delete(timed_release)
    db.session.commit()
    db.session.close()

    return redirect("/admin/timed_releases", code=303)


def process_timed_releases():
    # firstly, make challenges visible if their timed_release is in the past
    trs = db.session.query(TimedReleases).all()
    for tr in trs:
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        utc_release = tr.release.replace(tzinfo=datetime.timezone.utc)
        if utc_release > utc_now:
            # do nothing if release is in the future
            continue

        # change challenge to visible
        chall = db.session.query(Challenges).filter(Challenges.id == tr.chalid).first()
        chall.state = "visible"
        # delete used time_release
        db.session.delete(tr)

    # secondly, delete timed_releases for visible challenges (somebody could reveal challenges manually)
    chals = db.session.query(Challenges).filter(Challenges.state == "visible").all()
    for chal in chals:
        trs = db.session.query(TimedReleases).filter(TimedReleases.chalid == chal.id).all()
        for tr in trs:
            db.session.delete(tr)

    db.session.commit()
    db.session.close()
