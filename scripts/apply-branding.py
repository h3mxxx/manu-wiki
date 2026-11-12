#!/usr/bin/env python3
"""Apply the LuxPedia configuration through XWiki REST; default is a dry run."""
import argparse
import base64
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.xwiki.org'
ET.register_namespace('', NS)
N = '{' + NS + '}'


def node(name, value=None):
    element = ET.Element(N + name)
    element.text = value
    return element


def page_path(reference):
    parts = reference.split('.')
    quote = lambda value: urllib.parse.quote(value, safe='')
    return ''.join('/spaces/' + quote(part) for part in parts[:-1]) + '/pages/' + quote(parts[-1])


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('REST redirect refused; check XWIKI_URL')


class Branding:
    def __init__(self, apply=False):
        self.apply = apply
        base = os.environ.get('XWIKI_URL', 'http://127.0.0.1:8080').rstrip('/')
        parsed = urllib.parse.urlsplit(base)
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('XWIKI_URL must not contain credentials, a query or a fragment')
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', '::1')):
            raise ValueError('Use HTTPS except for the local isolated instance')
        self.base = base + '/rest/wikis/xwiki'
        user = (ROOT / '.secrets/admin_username').read_text().strip()
        password = (ROOT / '.secrets/admin_password').read_text().strip()
        self.auth = 'Basic ' + base64.b64encode(f'{user}:{password}'.encode()).decode()
        self.http = urllib.request.build_opener(NoRedirect)
        self.undo = []
        self.snapshot = None
        self.count = 0

    def request(self, path, method='GET', data=None, mime='application/xml'):
        headers = {'Authorization': self.auth, 'Content-Type': mime}
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with self.http.open(req, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code == 404 and method == 'GET':
                return None
            raise RuntimeError(f'{method} {path}: HTTP {error.code}') from None

    def change(self, label, path, method, data, before=None, mime='application/xml'):
        print(('APPLY ' if self.apply else 'PLAN  ') + label)
        self.count += 1
        if not self.apply:
            return
        # Journal before every mutation; no secrets or full preference objects are stored.
        if self.snapshot is None:
            folder = ROOT / '.runtime/branding'
            folder.mkdir(parents=True, exist_ok=True, mode=0o700)
            stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
            self.snapshot = folder / (stamp + '.json')
        self.undo.append({'label': label, 'path': path, 'before': before, 'mime': mime})
        self.snapshot.write_text(json.dumps({'base': self.base, 'changes': self.undo}, ensure_ascii=False, indent=2) + '\n')
        self.request(path, method, data, mime)

    def page(self, ref, title, content):
        path = page_path(ref)
        old = self.request(path)
        fields = {'title': title, 'syntax': 'xwiki/2.1', 'content': content}
        before = None
        if old:
            root = ET.fromstring(old)
            before = {key: root.findtext(N + key, '') for key in fields}
            if before == fields:
                return
        payload = node('page')
        payload.extend(node(key, value) for key, value in fields.items())
        self.change('page ' + ref, path, 'PUT', ET.tostring(payload), before)

    def objects(self, ref, cls):
        raw = self.request(page_path(ref) + '/objects')
        if raw is None:
            return []
        result = []
        for summary in ET.fromstring(raw).findall(N + 'objectSummary'):
            if summary.findtext(N + 'className') == cls:
                path = page_path(ref) + '/objects/' + cls + '/' + summary.findtext(N + 'number')
                xml = ET.fromstring(self.request(path))
                values = {p.attrib['name']: p.findtext(N + 'value', '') for p in xml.findall(N + 'property')}
                result.append((path, values))
        return result

    def obj(self, ref, cls, values, key=None):
        candidates = self.objects(ref, cls)
        if key:
            candidates = [(path, props) for path, props in candidates if props.get(key) == values[key]]
        if len(candidates) > 1:
            raise RuntimeError(f'Ambiguous object: {ref} / {cls}; inspect before changing')
        path, old = candidates[0] if candidates else (page_path(ref) + '/objects', {})
        changed = {key: str(value) for key, value in values.items() if str(value) != old.get(key)}
        if not changed:
            return
        payload = node('object')
        payload.append(node('className', cls))
        for key, value in changed.items():
            prop = node('property')
            prop.set('name', key)
            prop.append(node('value', value))
            payload.append(prop)
        before = {key: old.get(key, '') for key in changed} if candidates else None
        self.change('object ' + ref + ' / ' + cls, path, 'PUT' if candidates else 'POST', ET.tostring(payload), before)

    def attachment(self, ref, filename, source, mime):
        path = page_path(ref) + '/attachments/' + urllib.parse.quote(filename, safe='')
        old, new = self.request(path), source.read_bytes()
        if old != new:
            self.change('attachment ' + filename, path, 'PUT', new,
                        {'base64': base64.b64encode(old).decode()} if old else None, mime)

    def run(self):
        preferences = 'XWiki.XWikiPreferences'
        # Fail before writes if the Standard flavor or the expected theme is missing.
        theme = self.objects('FlamingoThemes.Iceberg', 'FlamingoThemesCode.ThemeClass')
        if len(theme) != 1 or not self.objects(preferences, 'XWiki.XWikiPreferences'):
            raise RuntimeError('Install the documented Standard flavor before applying branding')
        for filename in ('logo.svg', 'favicon.svg', 'favicon16.png', 'favicon144.png'):
            if not (ROOT / 'branding' / filename).is_file():
                raise RuntimeError('Missing branding asset: ' + filename)

        self.page('FlamingoThemes.LuxPedia', 'LuxPedia', '')
        values = dict(theme[0][1])
        values.update({'logo': 'logo.svg', 'logo-description': 'LuxPedia 企业知识库',
                       'navbar-default-bg': '#163c6a', 'brand-primary': '#2558a8'})
        self.obj('FlamingoThemes.LuxPedia', 'FlamingoThemesCode.ThemeClass', values)
        self.attachment('FlamingoThemes.LuxPedia', 'logo.svg', ROOT / 'branding/logo.svg', 'image/svg+xml')
        self.page('XWiki.LuxPediaSkin', 'LuxPedia', '')
        self.obj('XWiki.LuxPediaSkin', 'XWiki.XWikiSkins', {'name': 'LuxPedia', 'baseskin': 'flamingo', 'logo': 'logo.svg'})
        self.attachment('XWiki.LuxPediaSkin', 'logo.svg', ROOT / 'branding/logo.svg', 'image/svg+xml')
        for filename in ('favicon.svg', 'favicon16.png', 'favicon144.png'):
            self.attachment('XWiki.LuxPediaSkin', 'icons.xwiki.' + filename, ROOT / 'branding' / filename,
                            'image/svg+xml' if filename.endswith('.svg') else 'image/png')
        for ref in ('FlamingoThemes.LuxPedia', 'XWiki.LuxPediaSkin'):
            self.obj(ref, 'XWiki.XWikiRights', {'levels': 'edit,delete', 'groups': 'XWiki.XWikiAdminGroup', 'allow': '1'}, 'levels')
            # Only public brand assets need anonymous view, not knowledge pages.
            self.obj(ref, 'XWiki.XWikiRights', {'levels': 'view', 'groups': 'XWiki.XWikiAllGroup',
                     'users': 'XWiki.XWikiGuest', 'allow': '1'}, 'levels')

        for ref, title, filename in [('Main.WebHome', 'LuxPedia', 'home'),
                                     ('LuxPedia.Help.WebHome', 'LuxPedia 使用帮助', 'help'),
                                     ('LuxPedia.About.WebHome', '关于 LuxPedia', 'about')]:
            self.page(ref, title, (ROOT / 'branding/pages' / (filename + '.xwiki')).read_text())
        self.page('LuxPedia.WebHome', 'LuxPedia 帮助中心', '[[使用帮助>>LuxPedia.Help.WebHome]] · [[关于与开源声明>>LuxPedia.About.WebHome]]')
        self.page('LuxPedia.WebPreferences', 'LuxPedia 配置', '')
        self.obj('LuxPedia.WebPreferences', 'XWiki.XWikiGlobalRights',
                 {'levels': 'edit,delete', 'groups': 'XWiki.XWikiAdminGroup', 'allow': '1'}, 'levels')
        self.obj('LuxPedia.About.WebHome', 'XWiki.XWikiRights',
                 {'levels': 'view', 'groups': 'XWiki.XWikiAllGroup', 'users': 'XWiki.XWikiGuest', 'allow': '1'}, 'levels')

        self.page('LuxPedia.HelpPanel', 'LuxPedia 帮助', '')
        self.obj('LuxPedia.HelpPanel', 'Panels.PanelClass', {
            'name': 'LuxPedia 帮助', 'type': 'view', 'category': 'Information',
            'content': '{{velocity}}\n#panelheader("LuxPedia")\n* [[使用帮助>>LuxPedia.Help.WebHome]]\n* [[关于与开源声明>>LuxPedia.About.WebHome]]\n#panelfooter()\n{{/velocity}}',
            'async_cached': '0', 'async_enabled': '0'})

        self.obj('PanelsCode.ApplicationsPanelConfiguration', 'PanelsCode.ApplicationsPanelBlackListClass',
                 {'applicationId': 'platform.help'}, 'applicationId')
        self.obj('Tour.HomepageTour.WebHome', 'TourCode.TourClass', {'isActive': '0'})
        self.obj('WhatsNew.Code.NewsUIX', 'XWiki.UIExtensionClass', {'extensionPointId': ''})
        self.obj('XWiki.XWikiServerXwiki', 'XWiki.XWikiServerClass', {'wikiprettyname': 'LuxPedia'})
        self.obj(preferences, 'XWiki.XWikiPreferences', {
            'colorTheme': 'FlamingoThemes.LuxPedia', 'skin': 'XWiki.LuxPediaSkin',
            'title': "#if($xcontext.action == 'login')登录 - LuxPedia#elseif($tdoc.fullName == 'Main.WebHome')LuxPedia - 企业知识库#else$tdoc.getRenderedTitle('plain/1.0') - LuxPedia#end",
            'version': 'LuxPedia · 企业知识库 · <a href="$xwiki.getURL(\'LuxPedia.About.WebHome\')">关于与开源声明</a>',
            'rightPanels': 'Panels.MyRecentModifications,LuxPedia.HelpPanel'})
        print(f'{self.count} change(s); ' + ('applied' if self.apply else 'dry run; pass --apply to write'))
        if self.snapshot:
            print('Previous values saved to ' + str(self.snapshot.relative_to(ROOT)))


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='write the branding configuration')
    args = parser.parse_args()
    Branding(apply=args.apply).run()
