# -*- coding: utf-8 -*-
#
# Copyright: Simon Kowallik for the F5 DevCentral Community
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: f5os_restconf_config
short_description: Manage resources via the F5OS RESTCONF API.
description:
  - Manage resources via the F5OS RESTCONF API.
  - By default, this module will PUT the desired configuration to the specified URI.
author:
  - Simon Kowallik (@simonkowallik)
version_added: "1.0.0"
options:
  uri:
    description: The resource URI to work with.
    required: True
    type: str
  method:
    description: The HTTP method to use for modifying the resource.
    required: False
    type: str
    default: "PUT"
    choices:
        - "PUT"
        - "PATCH"
  state:
    description: The desired state of the resource.
    required: False
    type: str
    default: "present"
    choices:
        - "present"
        - "absent"
  config:
    description: The desired configuration to apply to the resource (PATCH) or to replace the resource with (PUT).
    required: False
    type: dict
  keys_ignore:
    description: A list of keys to ignore when comparing the current and desired configuration.
    required: False
    type: list
    elements: str
  config_query:
    description: A JMESPath query to filter the current configuration before it is compared to the desired configuration.
    required: False
    type: str
attributes:
    check_mode:
        description: The module supports check mode and will report what changes would have been made.
        support: full
    diff_mode:
        description: The module supports diff mode and will report the differences between the desired and actual state.
        support: full
notes:
    - This module requires the f5networks.f5os collection to be installed on the ansible controller.
    - This module uses the httpapi of the f5networks.f5os collection.
    - When using config_query jmespath module is required.
    - For better diff support, deepdiff module is recommended.
"""

EXAMPLES = r"""
- name: 'Set the login banner'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}/data/openconfig-system:system/config/login-banner"
    config:
      openconfig-system:login-banner: |-
        With great power comes great responsibility!
        -- Spider-man's grandpa

- name: 'Configure trunked VLANs'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}/data/openconfig-interfaces:interfaces/interface={{ item.interface }}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={{ item.id }}"
    state: "{{ item.state | default('present') }}"
    config:
      openconfig-vlan:trunk-vlans: ['{{ item.id }}']
  with_items:
    # Note: this is not an absolute list. Ansible will only "work" on the items below.
    # Any additional VLANs attached to the LAG will not be touched!
    - interface: my-lag
      id: 20
    - interface: 7.0
      id: 30
      state: absent  # Remove VLAN 30 from interface 7.0

- name: 'Partially configure LLDP'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}/data/openconfig-lldp:lldp/config"
    method: PATCH  # Use PATCH to partially update the configuration
    config:
      openconfig-lldp:config:
        # the PATCH method will only update these keys:
        enabled: 'true'
        f5-lldp:max-neighbors-per-port: 50
    keys_ignore:
      # keys_ignore has all remaining keys of this API endpoint.
      # The ansible module will therefore ignore the values in the
      # below keys when comparing the desired and current configuration.
      - f5-lldp:reinit-delay
      - f5-lldp:tx-delay
      - f5-lldp:tx-hold
      - f5-lldp:tx-interval
      - system-description
      - system-name
"""

RETURN = r"""
api_response:
    description: The API response received from the F5OS RESTCONF API. This is helpful when troubleshooting.
    returned: always
    type: dict
current_config_state:
    description: The current state and configuration of the resource as well as the API response of the initial GET (to retrieve the current state+configuration). This is helpful when troubleshooting.
    returned: always
    type: dict
desired_config_state:
    description: The desired state and configuration of the resource. This is helpful when troubleshooting.
    returned: always
    type: dict
changes:
    description: The changes made to the resource if any.
    returned: always
    type: dict
keys_ignore:
    description: The list of keys that were ignored while comparing the current configuration to the desired configuration.
    returned: when keys_ignore is set
    type: list
    elements: str
config_query:
    description: The JMESPath query used to filter the current configuration before it is compared to the desired configuration.
    returned: when config_query is set
    type: str
"""

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import ConnectionError

from ansible_collections.f5_ps_ansible.f5os.plugins.module_utils.json_query import (
    json_query,
)
from ansible_collections.f5_ps_ansible.f5os.plugins.module_utils.utils import (
    APIClient,
    changes_add_deep_diff,
    dicts_equal,
    format_bool_values,
    number_values_to_string,
    remove_state_property,
)


def main():
    """entry point for module execution"""
    argument_spec = dict(
        uri=dict(required=True, type="str"),
        config=dict(required=False, type="dict", default=None),
        method=dict(
            required=False, type="str", default="PUT", choices=["PUT", "PATCH"]
        ),
        state=dict(
            required=False, type="str", default="present", choices=["present", "absent"]
        ),
        keys_ignore=dict(required=False, type="list", default=[]),
        config_query=dict(required=False, type="str", default=""),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    result = {"changed": False, "failed": False, "keys_ignore": []}
    changes = {}  # default changes

    param_keys_ignore = module.params["keys_ignore"]
    param_config_query = module.params["config_query"]

    if param_keys_ignore:
        result.update({"keys_ignore": param_keys_ignore})

    if param_config_query:
        result.update({"config_query": param_config_query})

    desired_state = module.params["state"]
    current_state = "absent"
    desired_config = number_values_to_string(module.params["config"])
    desired_config = format_bool_values(desired_config)
    current_config = {}

    api_client = APIClient(module)
    try:
        api_response = api_client.get(uri=module.params["uri"])

        # get current state and configuration
        if api_response.get("code", 0) in [
            200,  # resource present
        ]:
            current_state = "present"
            current_config = remove_state_property(api_response.get("contents", {}))
            current_config = number_values_to_string(current_config)
            current_config = format_bool_values(current_config)

            if param_config_query:
                current_config = json_query(current_config, param_config_query)

        elif api_response.get("code", 0) in [
            404,  # resource absent
        ]:
            # element not found (could be an invalid path as well, which will fail later)
            current_config = {}
            current_state = "absent"
        elif api_response.get("code", 0) in [
            204,  # 20x response without content
        ] and not api_response.get("contents"):
            # element found but no content. A few APIs return 204 with no content when the configuration is missing.
            current_config = {}
            current_state = "absent"
        else:  # unsupported response codes
            module.fail_json(
                msg="Unsupported or unknown API response code.",
                **{"api_response": api_response},
            )

        # add current and desired state and configuration to the result for better troubleshooting
        result.update(
            {
                "current_config_state": {
                    "api_request": {
                        "method": "GET",
                        "uri": module.params["uri"],
                    },
                    "api_response": api_response,
                    "current_state": current_state,
                    "current_config": current_config,
                },
                "desired_config_state": {
                    "desired_config": desired_config,
                    "desired_state": desired_state,
                },
            }
        )

        # ansible check mode
        if module.check_mode:
            if desired_state == "present" and current_state == "absent":
                # we would create the resource
                changes.update({"before": {}, "after": desired_config})
            elif desired_state == "absent" and current_state == "present":
                # we would delete the resource
                changes.update({"before": current_config, "after": {}})
            elif desired_state == "present" and current_state == "present":
                # we would update the resource, if changed
                if not dicts_equal(current_config, desired_config, param_keys_ignore):
                    changes.update({"before": current_config, "after": desired_config})

            if module._diff:  # ansible --diff mode
                result.update({"diff": changes})

            if changes:
                changes_add_deep_diff(changes)
                result.update({"changed": True})

            result.update({"changes": changes})
            if param_keys_ignore:
                result.update({"keys_ignore": param_keys_ignore})

            module.exit_json(**result)

        # apply desired state and configuration
        if desired_state == "present":
            # check if a config change is required
            if not dicts_equal(current_config, desired_config, param_keys_ignore):
                if module.params["method"] == "PATCH":
                    api_response = api_client.patch(
                        uri=module.params["uri"], config=desired_config
                    )
                else:
                    api_response = api_client.put(
                        uri=module.params["uri"], config=desired_config
                    )

                if api_response.get("code", 0) not in [201, 204]:
                    result.update({"failed": True})
                else:
                    changes.update({"before": current_config, "after": desired_config})

        elif desired_state == "absent" and current_state == "present":
            # check if a delete is required
            api_response = api_client.delete(uri=module.params["uri"])

            if api_response.get("code", 0) not in [201, 204]:
                result.update({"failed": True})
            else:
                changes.update({"before": current_config, "after": {}})

    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))

    if module._diff:  # ansible --diff mode
        result.update({"diff": changes})

    if changes:
        changes_add_deep_diff(changes)
        result.update({"changed": True})

    result.update({"changes": changes})
    result.update({"api_response": api_response or {}})

    module.exit_json(**result)


if __name__ == "__main__":
    main()
