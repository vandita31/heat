# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from heat.engine import clients
from heat.engine.resources.neutron import neutron
from heat.engine import scheduler

if clients.neutronclient is not None:
    from neutronclient.common.exceptions import NeutronClientException

from heat.openstack.common import log as logging

logger = logging.getLogger(__name__)


class Firewall(neutron.NeutronResource):
    """
    A resource for the Firewall resource in Neutron FWaaS.
    """

    properties_schema = {'name': {'Type': 'String'},
                         'description': {'Type': 'String'},
                         'admin_state_up': {'Type': 'Boolean',
                                            'Default': True},
                         'firewall_policy_id': {'Type': 'String',
                                                'Required': True}}

    attributes_schema = {
        'id': 'unique identifier for the Firewall',
        'name': 'name for the Firewall',
        'description': 'description of the Firewall',
        'admin_state_up': 'the administrative state of the Firewall',
        'firewall_policy_id': 'unique identifier of the FirewallPolicy used to'
                              'create the Firewall',
        'status': 'the status of the Firewall',
        'tenant_id': 'Id of the tenant owning the Firewall'
    }

    update_allowed_keys = ('Properties',)
    update_allowed_properties = ('name', 'description', 'admin_state_up',
                                 'firewall_policy_id')

    def _show_resource(self):
        return self.neutron().show_firewall(self.resource_id)['firewall']

    def handle_create(self):
        props = self.prepare_properties(
            self.properties,
            self.physical_resource_name())
        firewall = self.neutron().create_firewall({'firewall': props})[
            'firewall']
        self.resource_id_set(firewall['id'])

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        if prop_diff:
            self.neutron().update_firewall(
                self.resource_id, {'firewall': prop_diff})

    def handle_delete(self):
        client = self.neutron()
        try:
            client.delete_firewall(self.resource_id)
        except NeutronClientException as ex:
            if ex.status_code != 404:
                raise ex
        else:
            return scheduler.TaskRunner(self._confirm_delete)()


class FirewallPolicy(neutron.NeutronResource):
    """
    A resource for the FirewallPolicy resource in Neutron FWaaS.
    """

    properties_schema = {'name': {'Type': 'String'},
                         'description': {'Type': 'String'},
                         'shared': {'Type': 'Boolean',
                                    'Default': False},
                         'audited': {'Type': 'Boolean',
                                     'Default': False},
                         'firewall_rules': {'Type': 'List',
                                            'Required': True}}

    attributes_schema = {
        'id': 'unique identifier for the FirewallPolicy',
        'name': 'name for the FirewallPolicy',
        'description': 'description of the FirewallPolicy',
        'firewall_rules': 'list of FirewallRules in this FirewallPolicy',
        'shared': 'shared status of this FirewallPolicy',
        'audited': 'audit status of this FirewallPolicy',
        'tenant_id': 'Id of the tenant owning the FirewallPolicy'
    }

    update_allowed_keys = ('Properties',)
    update_allowed_properties = ('name', 'description', 'shared',
                                 'audited', 'firewall_rules')

    def _show_resource(self):
        return self.neutron().show_firewall_policy(self.resource_id)[
            'firewall_policy']

    def handle_create(self):
        props = self.prepare_properties(
            self.properties,
            self.physical_resource_name())
        firewall_policy = self.neutron().create_firewall_policy(
            {'firewall_policy': props})['firewall_policy']
        self.resource_id_set(firewall_policy['id'])

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        if prop_diff:
            self.neutron().update_firewall_policy(
                self.resource_id, {'firewall_policy': prop_diff})

    def handle_delete(self):
        client = self.neutron()
        try:
            client.delete_firewall_policy(self.resource_id)
        except NeutronClientException as ex:
            if ex.status_code != 404:
                raise ex
        else:
            return scheduler.TaskRunner(self._confirm_delete)()


class FirewallRule(neutron.NeutronResource):
    """
    A resource for the FirewallRule resource in Neutron FWaaS.
    """

    properties_schema = {'name': {'Type': 'String'},
                         'description': {'Type': 'String'},
                         'shared': {'Type': 'Boolean',
                                    'Default': False},
                         'protocol': {'Type': 'String',
                                      'AllowedValues': ['tcp', 'udp', 'icmp',
                                                        None],
                                      'Default': None},
                         'ip_version': {'Type': 'String',
                                        'AllowedValues': ['4', '6'],
                                        'Default': '4'},
                         'source_ip_address': {'Type': 'String',
                                               'Default': None},
                         'destination_ip_address': {'Type': 'String',
                                                    'Default': None},
                         'source_port': {'Type': 'String',
                                         'Default': None},
                         'destination_port': {'Type': 'String',
                                              'Default': None},
                         'action': {'Type': 'String',
                                    'AllowedValues': ['allow', 'deny'],
                                    'Default': 'deny'},
                         'enabled': {'Type': 'Boolean',
                                     'Default': True}}

    attributes_schema = {
        'id': 'unique identifier for the FirewallRule',
        'name': 'name for the FirewallRule',
        'description': 'description of the FirewallRule',
        'firewall_policy_id': 'unique identifier of the FirewallPolicy to'
                              'which this FirewallRule belongs',
        'shared': 'shared status of this FirewallRule',
        'protocol': 'protocol value for this FirewallRule',
        'ip_version': 'ip_version for this FirewallRule',
        'source_ip_address': 'source ip_address for this FirewallRule',
        'destination_ip_address': 'destination ip_address for this'
                                  'FirewallRule',
        'source_port': 'source port range for this FirewallRule',
        'destination_port': 'destination port range for this FirewallRule',
        'action': 'allow or deny action for this FirewallRule',
        'enabled': 'indicates whether this FirewallRule is enabled or not',
        'position': 'position of the rule within the FirewallPolicy',
        'tenant_id': 'Id of the tenant owning the Firewall'
    }

    update_allowed_keys = ('Properties',)
    update_allowed_properties = ('name', 'description', 'shared',
                                 'protocol', 'ip_version', 'source_ip_address',
                                 'destination_ip_address', 'source_port',
                                 'destination_port', 'action', 'enabled')

    def _show_resource(self):
        return self.neutron().show_firewall_rule(
            self.resource_id)['firewall_rule']

    def handle_create(self):
        props = self.prepare_properties(
            self.properties,
            self.physical_resource_name())
        firewall_rule = self.neutron().create_firewall_rule(
            {'firewall_rule': props})['firewall_rule']
        self.resource_id_set(firewall_rule['id'])

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        if prop_diff:
            self.neutron().update_firewall_rule(
                self.resource_id, {'firewall_rule': prop_diff})

    def handle_delete(self):
        client = self.neutron()
        try:
            client.delete_firewall_rule(self.resource_id)
        except NeutronClientException as ex:
            if ex.status_code != 404:
                raise ex
        else:
            return scheduler.TaskRunner(self._confirm_delete)()


def resource_mapping():
    if clients.neutronclient is None:
        return {}

    return {
        'OS::Neutron::Firewall': Firewall,
        'OS::Neutron::FirewallPolicy': FirewallPolicy,
        'OS::Neutron::FirewallRule': FirewallRule,
    }
