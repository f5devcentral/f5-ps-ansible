---
title: Additional examples
parent: f5_ps_ansible.f5os
nav_order: 8
nav_enabled: true
---

{% raw %}

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
    # Note: this is not an absolute list. Ansible will only work on an item by item level.
    # Any additional VLANs attached to the LAG will not be touched!
    - interface: my-lag
      id: 20
      state: present
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
```

{% endraw %}
