---
title: API walkthrough - Ansible
parent: f5_ps_ansible.f5os
nav_order: 7
nav_enabled: true
---

{% raw %}

As you have completed the API walkthrough using the command line, below is an ansible playbook that performs exactly the same steps.

It's best to run it with very verbose debugging and step-by-step (tag by tag) to understand the underlying functionality of the ansible module.

Example:

```shell
ansible-playbook -vvv f5os_restconf_api_journey.yaml -t <step-X> -i <f5os_test_device>
```

You will still need a F5OS test device and a working ansible inventory pointing towards it.

```yaml
---
- name: 'F5OS RESTCONF API journey'
  connection: httpapi
  hosts: all
  gather_facts: false
  vars:
    # f5os api prefix determination based on https port
    f5os_api_prefix: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}"

  tasks:
    - name: '1. Retrieve /data/openconfig-system:system/dns'
      f5_ps_ansible.f5os.f5os_restconf_get:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
      tags: ['step-1']

    - name: 'Step 2. Add additional DNS resolvers'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
        config:
          openconfig-system:dns:
            config:
              search:
                - internal.example.net
            servers:
              server:
                - address: 8.8.4.4
                  config:
                    address: 8.8.4.4
                    port: 53
                - address: 8.8.8.8
                  config:
                    address: 8.8.8.8
                    port: 53
                - address: 9.9.9.9
                  config:
                    address: 9.9.9.9
                    port: 53
            host-entries:
              host-entry:
                - hostname: server.internal.example.net
                  config:
                    hostname: server.internal.example.net
                    ipv4-address:
                      - 192.0.2.10
      tags: ['step-2']

    - name: 'Step 3. Item-level resource declaration'
      block:
      - name: 'Step 3. Item-level resource declaration - GET'
        f5_ps_ansible.f5os.f5os_restconf_get:
          uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns/servers/server=9.9.9.9'
      - name: 'Step 3. Item-level resource declaration - PUT'
        vars:
          server:
            address: 9.9.9.10
            port: 53
        f5_ps_ansible.f5os.f5os_restconf_config:
          uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns/servers/server={{ server.address }}'
          config:
            openconfig-system:server:
              - address: "{{ server.address }}"
                config:
                  address: "{{ server.address }}"
                  port: "{{ server.port }}"  # no need to change to int, the type is ignored by the ansible module
      tags: ['step-3']

    # Step 4 is more complicated in ansible as we need to implement idempotency
    # and change detection not just blindly submit a PATCH request.
    - name: 'Step 4. Using PATCH'
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
      tags: ['step-4']

    - name: 'Step 5. PUT on dns/servers API endpoint'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns/servers'
        config:
          openconfig-system:servers:
            server:
              - address: 8.8.4.4
                config:
                  address: 8.8.4.4
                  port: 53
              - address: 8.8.8.8
                config:
                  address: 8.8.8.8
                  port: 53
              - address: 9.9.9.9
                config:
                  address: 9.9.9.9
                  port: 53
              - address: 9.9.9.10
                config:
                  address: 9.9.9.10
                  port: 53
              - address: 9.9.9.11
                config:
                  address: 9.9.9.11
                  port: 53
              - address: 149.112.112.112
                config:
                  address: 149.112.112.112
                  port: 53
      tags: ['step-5']

    - name: 'Step 6. Remove configuration resources declaratively'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns/servers'
        config:
          openconfig-system:servers:
            server:
              - address: 8.8.8.8
                config:
                  address: 8.8.8.8
                  port: 53
              - address: 9.9.9.9
                config:
                  address: 9.9.9.9
                  port: 53
              - address: 9.9.9.10
                config:
                  address: 9.9.9.10
                  port: 53
              - address: 9.9.9.11
                config:
                  address: 9.9.9.11
                  port: 53
      tags: ['step-6']

    - name: 'Step 7. Remove item-level resources'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns/servers'
        state: 'absent'  # <-- we want this resource to be absent on the system!
        config:
          openconfig-system:servers:
            server:
              - address: 8.8.8.8
                config:
                  address: 8.8.8.8
                  port: 53
      tags: ['step-7']
```

{% endraw %}