# -*- coding: utf-8 -*-
#
# Copyright: Simon Kowallik for the F5 DevCentral Community
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: f5os_restconf_post
short_description: POST to resources of the F5OS RESTCONF API.
description:
  - POST/Write to resources of the F5OS RESTCONF API.
author:
  - Simon Kowallik (@simonkowallik)
version_added: "1.3.0"
options:
  uri:
    description: The URI of the resource to write to.
    required: True
    type: str
  config:
    description: The desired configuration to apply to the resource (PATCH) or to replace the resource with (PUT).
    required: False
    type: dict
  secrets:
    description: A list of secrets to redact from the output. Any value in this list will be redacted with 'VALUE_SPECIFIED_IN_NO_LOG_PARAMETER'.
    required: False
    type: list
    elements: str
attributes:
    check_mode:
        description: The module does not support check mode.
        support: none
    diff_mode:
        description: The module does not support diff mode.
        support: none
notes:
    - This module requires the f5networks.f5os collection to be installed on the ansible controller.
    - This module uses the httpapi of the f5networks.f5os collection.
"""

EXAMPLES = r"""
- name: 'Update user password'
  vars:
    f5os_api_prefix: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}"
    f5os_username: admin
    f5os_password: "{{ lookup('env', 'F5OS_PASSWORD') }}"
  block:
    - name: 'Set user password'
      f5_ps_ansible.f5os.f5os_restconf_post:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/aaa/authentication/f5-system-aaa:users/f5-system-aaa:user={{ f5os_username }}/config/f5-system-aaa:set-password'
        config:
          f5-system-aaa:password: "{{ f5os_password }}"
        secrets:
          - "{{ f5os_password }}"
    - name: 'Get ansible_date_time variable'
      ansible.builtin.setup:
        gather_subset: [min]
    - name: 'Set last changed - prevents prompting to change password on next login'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/aaa/authentication/f5-system-aaa:users/f5-system-aaa:user={{ f5os_username }}/config'
        method: PATCH
        config:
          f5-system-aaa:config:
            last-change: "{{ ansible_date_time.date }}"
        config_query: |-
          "f5-system-aaa:config"."last-change" | { "f5-system-aaa:config": { "last-change": @ } }
"""

RETURN = r"""
api_response:
    description: The API response received from the F5OS RESTCONF API.
    returned: always
    type: dict
"""

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import ConnectionError

from ansible_collections.f5_ps_ansible.f5os.plugins.module_utils.utils import APIClient

from ansible_collections.f5_ps_ansible.f5os.plugins.module_utils.utils import (
    APIClient,
    format_bool_values,
    number_values_to_string,
)


def main():
    """entry point for module execution"""
    argument_spec = dict(
        uri=dict(required=True, type="str"),
        config=dict(required=False, type="dict", default=None),
        secrets=dict(required=False, type="list", default=[], no_log=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    result = {"changed": True, "failed": True}

    desired_config = number_values_to_string(module.params["config"])
    desired_config = format_bool_values(desired_config)

    api_client = APIClient(module)
    try:
        api_response = api_client.post(uri=module.params["uri"], config=desired_config)
        result.update({"api_response": api_response or {}})
        if api_response.get("code", 0) >= 200 and api_response.get("code", 0) < 300:
            result["failed"] = False
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))

    module.exit_json(**result)


if __name__ == "__main__":
    main()
