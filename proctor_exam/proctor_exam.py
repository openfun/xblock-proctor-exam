# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import re
import requests
import time
import pkg_resources

from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _

try:
    from contentstore.utils import get_lms_link_for_item
except ImportError:
    # we are on the LMS side, contentstore module is not in PYTHONPATH
    get_lms_link_for_item = None

from xblock.fields import String, Scope
from xblock.fragment import Fragment
from xblock.core import XBlock
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioContainerXBlockMixin

from lti_consumer.exceptions import LtiError
from lti_consumer.lti import LtiConsumer
from configurable_lti_consumer import ConfigurableLtiConsumerXBlock


API_URL = "https://fun.proctorexam.com/api/v3"


class ProctorExamXBlock(ConfigurableLtiConsumerXBlock, StudioContainerXBlockMixin):
    """
    This Xblock will restrain access to its children
    """

    has_children = True

    display_name = String(
        display_name=_("Display Name"),
        scope=Scope.settings,
        default="Proctor Exam",
    )

    lti_id = String(
        display_name=_("LTI ID"),
        scope=Scope.settings,
        default="proctor_exam",
    )

    def _is_studio(self):
        try:
            return self.runtime.is_author_mode
        except AttributeError:
            return False

    def user_is_staff(self):
        return getattr(self.runtime, 'user_is_staff', False)

    def get_icon_class(self):
        """
        Return the CSS class to be used in courseware sequence list.
        """
        return 'seq_problem'

    def resource_string(self, path):
        """
        Handy helper for getting resources from our package.
        """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def _render_template(self, ressource, context):
        """
        Render template with given context
        """
        template = Template(self.resource_string(ressource))
        html = template.render(Context(context))
        return html

    def _get_exam_id(self):
        """
        Return ProctorExam exam ID extracted from LTI launch URL
        """
        pattern = self.get_configuration(self.launch_url)["pattern"]
        match = re.match(pattern, self.launch_url)
        if match:
            try:
                return match.groupdict()["exam_id"]
            except KeyError:
                pass
        return None

    def get_proctorexam_user_state(self, exam_id, lti_parameters):
        """
        Retrieve user status from Proctor Exam API
        """
        endpoint_url = API_URL + "/exams/%s/show_lti_student" % exam_id
        api_token, secret_key = self.lti_provider_key_secret
        if not api_token:
            return {"errors": _("LTI passport is not configured")}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Token token=%s" % api_token,
            "Accept": "application/vnd.procwise.v3"
        }
        params = {
            "nonce": int(time.time()),
            "timestamp": int(time.time() * 1000),
            "id": exam_id,
            "student_lms_id": lti_parameters["user_id"],
            "resource_link_id": lti_parameters["resource_link_id"],
            "context_id": lti_parameters["context_id"],
        }
        fields = "?".join(["%s=%s" % (key, value) for key, value in sorted(params.items())])
        signature = hmac.new(secret_key.encode(), fields.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature

        response = requests.get(endpoint_url, headers=headers, data=json.dumps(params))
        try:
            json_response = json.loads(response.content)
        # API returns an HTML page about browser compatibility if user is yet unknown,
        # so we handle this case ourselves
        except ValueError:
            json_response = {"student": {"status": "not_setup"}}
        return json_response

    def author_edit_view(self, context):
        """
        We override this view from StudioContainerXBlockMixin to allow
        the addition of children xblocks, by passing can_add=True to
        render_children, Studio will add big green buttons to the page
        """
        fragment = Fragment()
        self.render_children(context, fragment, can_reorder=True, can_add=True)
        return fragment

    def _get_context_for_template(self):
        """
        Add needed values to template context
        """
        context = super(ProctorExamXBlock, self)._get_context_for_template()
        context.update({
            'user_is_staff': self.user_is_staff(),
            "banner": self.runtime.local_resource_url(self, 'public/images/banner.png'),
            "chrome_logo": self.runtime.local_resource_url(self, 'public/images/chrome-logo.png'),
            "warning_icon": self.runtime.local_resource_url(self, 'public/images/warning-icon.png'),
        })
        return context

    def student_view(self, context=None):
        user_allowed = False
        user_state = {}
        message = ""
        lti_parameters = {}
        fragment = Fragment()
        context = self._get_context_for_template()
        child_fragments = self.runtime.render_children(block=self, view_name='student_view')
        context.update({"child_fragments": child_fragments})

        if self._is_studio():  # studio view
            context["lms_link"] = get_lms_link_for_item(self.location) if get_lms_link_for_item else ""
            fragment.add_content(self._render_template('static/html/studio.html', context))
        else:  # Student view
            if self.launch_url and self._get_exam_id():
                try:
                    lti_consumer = LtiConsumer(self)
                    lti_parameters = lti_consumer.get_signed_lti_parameters()
                    exam_id = self._get_exam_id()
                    user_state = self.get_proctorexam_user_state(
                        self._get_exam_id(),
                        lti_parameters
                    )
                    context["user_state"] = user_state
                except LtiError:
                    message = _("Proctor Exam xblock configuration is incomplete, LTI passport is invalid")
            else:
                message = _("Proctor Exam xblock configuration is incomplete, exam URL is missing")

            if user_state and "student" in user_state and (user_state["student"].get("status") == "exam_started"):
                # User have completed Proctor Exam indentification process,
                # we show him exam content
                html = self._render_template('static/html/sequence.html', context)
                fragment.add_content(html)
                fragment.add_frags_resources(child_fragments)
            else:
                # User have to complete Proctor Exam indentification process
                context.update({'lti_parameters': lti_parameters, "message": message})
                html = self._render_template("static/html/student.html", context)
                fragment.add_content(html)
                fragment.add_css(self.resource_string('static/css/student.css'))

        return fragment
