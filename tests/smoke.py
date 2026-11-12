"""Read-only checks for the seeded POC; credentials remain local and unprinted."""
import base64
import hashlib
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('XWIKI_URL', 'http://127.0.0.1:8080').rstrip('/')
REST = BASE + '/rest/wikis/xwiki'
PUBLISHED = '/spaces/Knowledge/spaces/Technical/pages/WebHome'
DRAFT = '/spaces/Drafts/spaces/Secret/pages/WebHome'
ATTACHMENTS = '/spaces/Knowledge/spaces/Attachments/pages/WebHome/attachments/'


def get(path, user=None):
    headers = {}
    if user:
        if user == 'admin':
            name = (ROOT / '.secrets/admin_username').read_text().strip()
            password_file = ROOT / '.secrets/admin_password'
        else:
            name = user
            password_file = ROOT / f'.secrets/{user}_password'
        auth = base64.b64encode(f'{name}:{password_file.read_text().strip()}'.encode()).decode()
        headers['Authorization'] = 'Basic ' + auth
    try:
        with urlopen(Request(REST + path, headers=headers), timeout=30) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


class WikiSmoke(unittest.TestCase):
    def test_reader_can_read_published_page(self):
        status, body = get(PUBLISHED, 'pocreader')
        self.assertEqual(status, 200)
        self.assertIn(b'MANU-WIKI-PUBLISHED-20261112', body)

    def test_editor_and_reviewer_can_read_draft(self):
        for user in ('poceditor', 'pocreviewer'):
            with self.subTest(user=user):
                status, body = get(DRAFT, user)
                self.assertEqual(status, 200)
                self.assertIn(b'MANU-WIKI-DRAFT-PRIVATE-20261112', body)

    def test_reader_cannot_read_draft(self):
        status, body = get(DRAFT, 'pocreader')
        self.assertIn(status, (401, 403, 404))
        self.assertNotIn(b'MANU-WIKI-DRAFT-PRIVATE-20261112', body)

    def test_guest_cannot_read_pages_or_attachments(self):
        for path in (PUBLISHED, DRAFT, ATTACHMENTS + 'sample.docx'):
            with self.subTest(path=path):
                status, body = get(path)
                self.assertIn(status, (401, 403, 404))
                self.assertNotIn(b'MANU-WIKI-PUBLISHED-20261112', body)
                self.assertNotIn(b'MANU-WIKI-DRAFT-PRIVATE-20261112', body)

    def test_attachments_match_uploaded_bytes(self):
        for name in ('architecture.svg', 'sample.pdf', 'sample.docx', 'sample.mp4'):
            with self.subTest(name=name):
                status, body = get(ATTACHMENTS + name, 'pocreader')
                self.assertEqual(status, 200)
                self.assertEqual(hashlib.sha256(body).digest(),
                                 hashlib.sha256((ROOT / 'examples/attachments' / name).read_bytes()).digest())

    def test_workflow_published_copy_and_draft_acl(self):
        status, body = get('/spaces/Knowledge/spaces/WorkflowDemo/pages/WebHome', 'pocreader')
        self.assertEqual(status, 200)
        self.assertIn(b'MANU-WORKFLOW-PUBLISHED-20261112', body)
        page = ET.fromstring(body)
        self.assertEqual(page.findtext('{http://www.xwiki.org}author'), 'XWiki.pocreviewer')
        status, body = get('/spaces/Drafts/spaces/WorkflowDemo/pages/WebHome', 'pocreader')
        self.assertIn(status, (401, 403, 404))
        self.assertNotIn(b'MANU-WORKFLOW-PUBLISHED-20261112', body)

    def test_browser_rollback_result_is_preserved(self):
        status, body = get('/spaces/Drafts/spaces/EditorDemo/pages/WebHome', 'poceditor')
        self.assertEqual(status, 200)
        page = ET.fromstring(body)
        content = page.findtext('{http://www.xwiki.org}content', '')
        self.assertIn('MANU-EDITOR-V1', content)
        self.assertNotIn('MANU-EDITOR-V2', content)
        self.assertEqual(page.findtext('{http://www.xwiki.org}version'), '3.1')

    def test_page_history_is_available(self):
        status, body = get(PUBLISHED + '/history', 'admin')
        self.assertEqual(status, 200)
        self.assertIn(b'version', body)


if __name__ == '__main__':
    unittest.main(verbosity=2)
