# -*- coding: utf-8 -*-
#
# Copyright: Simon Kowallik for the F5 DevCentral Community
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: f5os_restconf_get
short_description: Get resources from the F5OS RESTCONF API.
description:
  - Get/Read resources from the F5OS RESTCONF API.
author:
  - Simon Kowallik (@simonkowallik)
version_added: "1.0.0"
options:
  uri:
    description: The URI of the resource to read.
    required: True
    type: str
attributes:
    check_mode:
        description: The module supports check mode and will report what changes would have been made.
        support: full
    diff_mode:
        description: The module supports diff mode and will report the differences between the desired and actual state.
        support: none
notes:
    - This module requires the f5networks.f5os collection to be installed on the ansible controller.
    - This module uses the httpapi of the f5networks.f5os collection.
"""

EXAMPLES = r"""
- name: "F5OS API: Wait till ready"
  f5_ps_ansible.f5os.f5os_restconf_get:
    uri: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}/data/openconfig-system:system/f5os-system-version:version"
  retries: "{{ f5os_api_restart_handler.retries }}"
  delay: "{{ f5os_api_restart_handler.delay }}"

- name: "Get clock API data"
  f5_ps_ansible.f5os.f5os_restconf_get:
    uri: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}/data/openconfig-system:system/clock"
  register: clock_config_state

- name: "Display clock config and state"
  ansible.builtin.debug:
    var: clock_config_state
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


def main():
    """entry point for module execution"""
    argument_spec = dict(
        uri=dict(required=True, type="str"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    result = {"changed": False, "failed": False}

    api_client = APIClient(module)
    try:
        api_response = api_client.get(uri=module.params["uri"])
        result.update({"api_response": api_response or {}})
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))

    module.exit_json(**result)


if __name__ == "__main__":
    main()
