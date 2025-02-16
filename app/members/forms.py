#!/usr/bin/env python
# encoding: utf-8
from django import forms
from django.contrib.auth.models import User
from localflavor.br.forms import BRCPFField, BRPhoneNumberField

from django.forms import TextInput
from django.forms.utils import flatatt

from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Organization, Member, Category


class OrganizationInput(TextInput):
    def _format_value(self, value):
        if type(value) is not int:
            return value
        try:
            organization = Organization.objects.get(id=value)
            value = organization.name
        except Organization.DoesNotExist:
            value = ''
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = self._format_value(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class UserForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First Name"))
    last_name = forms.CharField(label=_("Last Name"))
    email = forms.CharField(label=_("Email"))

    class Meta:
        model = User
        exclude = ('username', )
        fields = ('first_name', 'last_name', 'email')


class MemberForm(forms.ModelForm):
    cpf = BRCPFField(label=_("CPF"), required=True)
    phone = BRPhoneNumberField(label=_("Phone"), required=False)
    github_user = forms.CharField(label=_("GitHub User"), required=False)
    organization = forms.CharField(label=_("Organization"), widget=OrganizationInput, required=False)
    location = forms.CharField(label=_("Location"), required=False)


    class Meta:
        model = Member
        exclude = ('user', )
        fields = ('category', 'github_user', 'organization', 'cpf', 'phone', 'address', 'location', 'relation_with_community', 'mailing', 'partner')

    def clean_organization(self):
        organization = self.cleaned_data['organization']
        if not organization:
            return None
        organization_instance, created = Organization.objects.get_or_create(name=organization)
        return organization_instance

    def save(self, user, commit=True):
        self.instance.user = user
        return super(MemberForm, self).save(commit)
