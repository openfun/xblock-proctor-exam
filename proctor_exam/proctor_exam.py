# -*- coding: utf-8 -*-

import datetime
import pkg_resources

from django.template import Context, Template
from django.utils.translation import ugettext_lazy, ugettext as _

from xblock.fields import String, Scope
#from web_fragments.fragment import Fragment
from xblock.fragment import Fragment
from xblock.core import XBlock
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioContainerXBlockMixin

from lti_consumer.lti import LtiConsumer
from configurable_lti_consumer import ConfigurableLtiConsumerXBlock


class ProctorExamXBlock(ConfigurableLtiConsumerXBlock, StudioContainerXBlockMixin):
    """
    This Xblock will restrain access to its children
    """

    has_children = True

    display_name = String(
        display_name=_("Display Name"),
        scope=Scope.settings,
        default=_("Proctor Exam"),
    )

    def _is_studio(self):
        try:
            return self.runtime.is_author_mode
        except AttributeError:
            return False

    def user_is_staff(self):
        return getattr(self.runtime, 'user_is_staff', False)

    def get_icon_class(self):
        """Return the CSS class to be used in courseware sequence list."""
        return 'seq_problem'

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def _render_template(self, ressource, **kwargs):
        template = Template(self.resource_string(ressource))
        context = dict({
                'user_is_staff': self.user_is_staff(),
                'user_allowed': self.is_user_allowed(),
                },
                **kwargs)
        html = template.render(Context(context))
        return html

    def is_user_allowed(self):
        """
        Is LMS user correctly indentified on Proctor Exam
        """
        return False

    def student_view(self, context=None):
        fragment = Fragment()
        child_fragments = self.runtime.render_children(block=self, view_name='student_view')
        context = self._get_context_for_template()
        context.update({"child_fragments": child_fragments})

        if self._is_studio():  # studio view
            fragment.add_content(ragment(self._render_template('static/html/studio.html', **context)))
            return fragment
        else:  # student view
            if self.is_user_allowed():
                html = self._render_template('static/html/sequence.html', **context)
                fragment.add_content(html)
                fragment.add_frags_resources(child_fragments)
                return fragment
            else:
                lti_consumer = LtiConsumer(self)
                lti_parameters = lti_consumer.get_signed_lti_parameters()
                context.update({'lti_parameters': lti_parameters})
                html = self._render_template("static/html/student.html", **context)
                fragment.add_content(html)

                return fragment
