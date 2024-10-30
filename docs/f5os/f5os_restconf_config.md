---
title: f5os_restconf_config
parent: f5_ps_ansible.f5os
nav_order: 100
nav_enabled: true
---
{% raw %}

# f5os_restconf_config

**Short Description:** Manage resources via the F5OS RESTCONF API.

**Description:**

- Manage resources via the F5OS RESTCONF API.
- By default, this module will PUT the desired configuration to the specified URI.

**Author:** Simon Kowallik (@simonkowallik)

**Version Added:** 1.0.0

## Options

| Option | Description | Required | Type | Default | Choices |
|--------|-------------|----------|------|---------|---------|
| uri | The resource URI to work with. | True | `str` |  |  |
| method | The HTTP method to use for modifying the resource. | False | `str` | `PUT` | `PUT, PATCH` |
| state | The desired state of the resource. | False | `str` | `present` | `present, absent` |
| config | The desired configuration to apply to the resource (PATCH) or to replace the resource with (PUT). | False | `dict` |  |  |
| keys_ignore | A list of keys to ignore when comparing the current and desired configuration. This is useful when only a subset of the configuration is desired to be compared. The keys are ignored for the comparison only, not for the actual configuration. The keys will be ignored recursively in the desired configuration and current configuration. | False | `list` |  |  |
| config_query | A JMESPath query to filter the current configuration before it is compared to the desired configuration. | False | `str` |  |  |

## Attributes

| Attribute | Support | Description |
|-----------|---------|-------------|
| Check_mode | full | The module supports check mode and will report what changes would have been made. |
| Diff_mode | full | The module supports diff mode and will report the differences between the desired and actual state. |

## Notes

- This module requires the f5networks.f5os collection to be installed on the ansible controller.
- This module uses the httpapi of the f5networks.f5os collection.
- When using config_query jmespath module is required.
- For better diff support, deepdiff module is recommended.

## Return Values

| Key | Description | Returned | Type | Elements |
|-----|-------------|----------|------|----------|
| api_response | The API response received from the F5OS RESTCONF API. This is helpful when troubleshooting. | always | `dict` |  |
| current_config_state | The current state and configuration of the resource as well as the API response of the initial GET (to retrieve the current state+configuration). This is helpful when troubleshooting. | always | `dict` |  |
| desired_config_state | The desired state and configuration of the resource. This is helpful when troubleshooting. | always | `dict` |  |
| changes | The changes made to the resource if any. | always | `dict` |  |
| keys_ignore | The list of keys that were ignored while comparing the current configuration to the desired configuration. | when keys_ignore is set | `list` | `str` |
| config_query | The JMESPath query used to filter the current configuration before it is compared to the desired configuration. | when config_query is set | `str` |  |

## Examples

```yaml

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

- name: 'Using PATCH on a group of resources (list) with additional config endpoints'
  vars:
    server:
      address: 9.9.9.11
      port: 53
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
    method: 'PATCH'
    # For change detection and idempotency to work we will need to filter the API response.
    # This can be done using the below "config_query" using a jmespath query, 
    # the jmespath module is required!
    #
    # As the API returns the whole list of resources (dns servers) possibly along with
    # 'host-entries' and 'config', we need to reduce the response to the item we expect
    # to be created by the PATCH operation.
    # f5os_restconf_config must be able to compare the API response (current_config) to
    # the desired configuration (desired_config)
    config_query: |-
      "openconfig-system:dns".servers.server[?address == '{{ server.address }}'] | { "openconfig-system:dns": { servers: { server: @ } } }
    config:
      openconfig-system:dns:
        servers:
          server:
            - address: "{{ server.address }}"
              config:
                address: "{{ server.address }}"
                port: "{{ server.port }}"  # no need to change to int, the type is ignored by the ansible module
```

{% endraw %}
