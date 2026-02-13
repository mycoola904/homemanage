from pathlib import Path

from django.test import SimpleTestCase


class TemplateSafetyTests(SimpleTestCase):
    def test_touched_templates_do_not_use_multiline_django_comment_blocks(self):
        template_paths = [
            Path("templates/components/layout/app.html"),
            Path("templates/components/layout/navbar.html"),
            Path("templates/components/layout/sidebar.html"),
            Path("templates/pages/household_home.html"),
            Path("templates/pages/no_household_access.html"),
        ]

        for template_path in template_paths:
            content = template_path.read_text(encoding="utf-8")
            self.assertNotIn("{% comment %}", content, msg=f"{template_path} contains multiline comment blocks")
            self.assertNotIn("{% endcomment %}", content, msg=f"{template_path} contains multiline comment blocks")
