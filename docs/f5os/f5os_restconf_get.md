---
title: f5os_restconf_get
parent: f5_ps_ansible.f5os
nav_order: 101
nav_enabled: true
---
{% raw %}

# f5os_restconf_get

**Short Description:** Get resources from the F5OS RESTCONF API.

**Description:**

- Get/Read resources from the F5OS RESTCONF API.

**Author:** Simon Kowallik (@simonkowallik)

**Version Added:** 1.0.0

## Options

| Option | Description | Required | Type | Default / Choices |
|--------|-------------|----------|------|-----------------|
| `uri` | The URI of the resource to read. | `true` | `str` |   |

## Attributes

| Attribute | Support | Description |
|-----------|---------|-------------|
| `check_mode` | full | The module supports check mode and will report what changes would have been made. |
| `diff_mode` | none | The module supports diff mode and will report the differences between the desired and actual state. |

## Notes

- This module requires the f5networks.f5os collection to be installed on the ansible controller.
- This module uses the httpapi of the f5networks.f5os collection.

## Return Values

| Key | Description | Returned | Type | Elements |
|-----|-------------|----------|------|----------|
| `api_response` | The API response received from the F5OS RESTCONF API. | always | `dict` |  |

## Examples

```yaml

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
```

{% endraw %}
