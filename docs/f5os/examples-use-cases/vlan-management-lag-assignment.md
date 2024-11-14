---
title: VLAN management and LAG assignment
parent: Examples / Use-Cases
nav_order: 2
nav_enabled: true
---
{% raw %}

# VLAN management and LAG assignment

[The below is available as an example role in the repository.](https://github.com/f5devcentral/f5-ps-ansible/tree/main/examples/roles)

## 1. Item-level declarative VLAN resources, add VLANs to their desired LAG

```yaml
# Task utilizing the role and assigning config parameters, typically used in a playbook
- name: 'Create VLANs and assign to LAGs'
  vars:
    my_vlans:  # item-by-item declarative, the list absolute per item but not in total
      - name: vlan-explict-present
        id: 1
        lag: lag-portchannel1
        state: present  # explicit state
      - name: vlan-implict-present 
        id: 2
        lag: lag-portchannel1
        # no state key, implict state is present by default.
      - name: vlan-explict-absent
        id: 3
        lag: lag-portchannel1
        state: absent  # state is absent, vlan will be removed from LAG and VLANs
  include_role:
    name: f5os_vlan
  loop: '{{ my_vlans }}'
  loop_control:
    loop_var: f5os_vlan_config
```

The above implementation iterates over the provided VLAN list `my_vlans`. It will only work on an item-by-item (VLAN by VLAN) basis, hence **it will allow additional VLANs to co-exist** (eg. created/maintained by other automation systems).

As we create VLANs and plan to assign them to a LAG (or interface), we need to take the order of operation into account.

**Creation**

1. Create VLAN
2. Assign to LAG/Interface

**Removal**

1. Remove VLAN from LAG/Interface
2. Delete VLAN

{: .note }
When dealing with removing a VLAN in practice one needs to consider removing them from Tenants as well. This could be achieved by creating a playbook that first deals with VLAN removal from a Tenant before continuing to remove the VLAN from F5OS, similar to the below approach.

Focusing on VLAN and LAG, the below role task would allow creation and removal in order.

```yaml
# roles/f5os_vlan/tasks/main.yaml
---
- name: 'Create VLAN and add to LAG'
  when: (f5os_vlan_config.state is not defined or f5os_vlan_config.state == 'present')
  block:
    - name: 'Create VLAN'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-vlan:vlans/vlan={{ f5os_vlan_config.id }}"
        state: "{{ f5os_vlan_config.state | default('present') }}"
        config:
          openconfig-vlan:vlan:
            - vlan-id: "{{ f5os_vlan_config.id }}"
              config:
                vlan-id: "{{ f5os_vlan_config.id }}"
                name: "{{ f5os_vlan_config.name }}"
        keys_ignore:
          - members

    - name: 'Configure trunked VLAN on LAG'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-interfaces:interfaces/interface={{ f5os_vlan_config.lag }}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={{ f5os_vlan_config.id }}"
        state: "{{ f5os_vlan_config.state | default('present') }}"
        config:
          openconfig-vlan:trunk-vlans: ['{{ f5os_vlan_config.id }}']

- name: 'Delete VLAN and remove from LAG'
  when: f5os_vlan_config.state == 'absent'
  block:
    - name: 'Remove VLAN from LAG'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-interfaces:interfaces/interface={{ f5os_vlan_config.lag }}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={{ f5os_vlan_config.id }}"
        state: absent

    - name: 'Delete VLAN'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-vlan:vlans/vlan={{ f5os_vlan_config.id }}"
        state: absent
```

{: .note }
The F5OS RESTCONF API adds a `members` object to a VLAN that has been assigned to an interface/LAG that contains `state` about the usage of the VLAN. For an example response of the `/data/openconfig-vlan:vlans` resource illustrating the difference, see below.

<p><details close markdown="block"><summary>/data/openconfig-vlan:vlans example response</summary>
```json
{
  "openconfig-vlan:vlans": {
    "vlan": [
      {
      "vlan-id": 1,
      "config": { "vlan-id": 1, "name": "my-assigned-vlan-1" },
--->      "members": {
--->        "member": [ { "state": { "interface": "lag-portchannel1" } } ]
--->      }
      },
      {
      "vlan-id": 2,
      "config": { "vlan-id": 2, "name": "my-unassigned-vlan-2" }
      }
    ]
  }
}
```
</details></p>

## 2. Fully declarative VLAN resources, add VLANs to their desired LAG

What is our desired goal?

- Assume complete control and authority of all VLANs
- Assign VLANs to a single LAG

The below task illustrates all desired VLANs.

{: .note }
Note that while the VLAN resource is fully declared (the below is the complete configuration desired on the system, no additional VLANs), we still require an ansible `state` setting as we want to make sure that VLANs are removed from LAGs when the are removed.

```yaml
# Task utilizing the role and assigning config parameters, typically used in a playbook
- name: 'Create VLANs and assign to LAGs'
  vars:
    f5os_vlan_declarative_config:
      - name: vlan-explict-present 
        id: 1
        lag: lag-portchannel1
        state: present  # explicit state
      - name: vlan-implict-present 
        id: 2
        lag: lag-portchannel1
        # no state key, implict state is present by default.
      - name: vlan-explict-absent
        id: 3
        lag: lag-portchannel1
        state: absent  # Note state absent is absent!
  include_role:
    name: f5os_vlan_declarative
```

Below is the tasks file of the role.

{: .note }
Note the task order and filtering of desired and undesired vlans.

```yaml
# roles/f5os_vlan_declarative/tasks/main.yaml
---
# remove any undesired VLANs
- name: 'Remove VLAN from LAG'
  vars:
    # extract vlans to remove (state=absent)
    undesired_vlans: "{{ f5os_vlan_declarative_config | selectattr('state', 'defined') | selectattr('state', 'eq', 'absent') | list }}"
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-interfaces:interfaces/interface={{ item.lag }}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={{ item.id }}"
    state: absent
  with_items: "{{ undesired_vlans }}"

# fully declare the VLAN resource
- name: 'Create VLAN'
  vars:
    # extract desired vlans, either state=present or state not defined (present is the default)
    desired_vlans: "{{ f5os_vlan_declarative_config | selectattr('state', 'undefined') | list + f5os_vlan_declarative_config | selectattr('state', 'defined') | selectattr('state', 'eq', 'present') | list }}"
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-vlan:vlans"
    config: "{{ lookup('ansible.builtin.template', './templates/vlans.yaml.j2') | from_yaml }}"
    keys_ignore:
      - members

# add VLANs one-by-one to the desired LAG
- name: 'Add VLAN to LAG'
  vars:
    # extract desired vlans, either state=present or state not defined (present is the default)
    desired_vlans: "{{ f5os_vlan_declarative_config | selectattr('state', 'undefined') | list + f5os_vlan_declarative_config | selectattr('state', 'defined') | selectattr('state', 'eq', 'present') | list }}"
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ f5os_api_prefix | default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-interfaces:interfaces/interface={{ item.lag }}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={{ item.id }}"
    config:
      openconfig-vlan:trunk-vlans: ['{{ item.id }}']
  with_items: "{{ desired_vlans }}"

```

{% endraw %}
