"""Copyright 2008 Orbitz WorldWide

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""
import calendar
import hashlib
import pytz


def is_pattern(s):
    return '*' in s or '?' in s or '[' in s or '{' in s


def hash_request():
    keys = set()
    if request.json:
        keys.update(request.json.keys())
    if request.form:
        keys.update(request.form.keys())
    keys.update(request.args.keys())
    params = u",".join([
        u"{0}={1}".format(key, u"&".join(sorted(RequestParams.getlist(key))))
        for key in sorted(keys) if not key.startswith('_')
    ])
    md5 = hashlib.md5()
    md5.update(params.encode('utf-8'))
    return md5.hexdigest()


def to_seconds(delta):
    return abs(delta.seconds + delta.days * 86400)


def epoch(dt):
    """
    Returns the epoch timestamp of a timezone-aware datetime object.
    """
    return calendar.timegm(dt.astimezone(pytz.utc).timetuple())
