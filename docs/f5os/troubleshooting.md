---
title: Troubleshooting
parent: f5_ps_ansible.f5os
nav_order: 8
nav_enabled: true
---
{% raw %}

# Troubleshooting

First steps:

1. Focus on a single failing task to limit the information that needs to be analyzed
2. Run ansible with `-vvv` or even `-vvvv` verbosity
3. Add `ansible.builtin.debug` for better filtering of task outputs
4. Analyze the `f5os_restconf_config` module output based on the below demo
5. Use an API client to understand the behavior of the API without added behavior by ansible but keep the modification applied to the API response by the module in mind!

{: .note }
> Due to the large amount of debug data the below output is abbreviated and verbose sections are collapsed by default.
>
> The displayed JSON is also not valid, many `,` commas have been removed for the syntax highlighter to work properly.

## Scenario

Assume the below is configured for the `/data/openconfig-system:system/dns` resource.

```json
{
  "openconfig-system:dns": {
    "config": {
      "search": ["internal.example.net"]
    },
    "servers": {
        "server": [
            {"address": "8.8.8.8", "config":{"address": "8.8.8.8", "port": 53}},
            {"address": "9.9.9.9", "config":{"address": "9.9.9.9", "port": 53}}
        ]
    },
    "host-entries": {
        "host-entry": [{"hostname": "server.internal.example.net",
             "config": {"hostname": "server.internal.example.net",
                        "ipv4-address":["192.0.2.10"]}
        }]
    }
  }
}
```

### Chapter One - Attempt 1

Assume we decided to use the PATCH method to add an additional DNS resolver `9.9.9.10`.

Running the below succeeds, the server is added (check the GUI, CLI and/or API).

```yaml
- name: 'Chapter One - Attempt 1'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
    method: 'PATCH'
    config:
      openconfig-system:dns:
        servers:
          server:
            - address: 9.9.9.10
              config:
                address: 9.9.9.10
                port: 53
  tags: ['try-1']
```

However when running the task again, ansible reports `changed=1`, so what is the problem?

Let's run it again, this time enabling debugging:

```shell
ansible-playbook <playbook.yaml> -i <f5os_device> -t attempt-1 -vvv
```

The below `"api_response"` object describes the response received from the F5OS API. In this case it is the response to the PATCH request. Contents is typically empty when a config operation was successful. On errors it usually carries more information.

```json
{
  "api_response": {
    "code": 204,
    "contents": {},
    "headers": "omitted for brevity"
  },
  "changed": true,
  "changes": {
    "after": {
```

<p><details close markdown="block"><summary>expand</summary>
```json
      "openconfig-system:dns": {
        "servers": {
          "server": [
            {
              "address": "9.9.9.10",
              "config": { "address": "9.9.9.10", "port": "53" }
            }
          ]
        }
      }
```
</details></p>

```json
    "before": {
```

<p><details close markdown="block"><summary>expand</summary>
```json
      "openconfig-system:dns": {
        "config": {
          "search": ["internal.example.net"]
        },
        "host-entries": {
          "host-entry": [
            {
              "config": {
                "hostname": "server.internal.example.net",
                "ipv4-address": ["192.0.2.10"]
              },
              "hostname": "server.internal.example.net"
            }
          ]
        },
        "servers": {
          "server": [
            {
              "address": "8.8.8.8",
              "config": {
                "address": "8.8.8.8",
                "port": "53"
              }
            },
            {
              "address": "9.9.9.9",
              "config": {
                "address": "9.9.9.9",
                "port": "53"
              }
            },
            {
              "address": "9.9.9.10",
              "config": {
                "address": "9.9.9.10",
                "port": "53"
              }
            }
          ]
        }
      }
```
</details></p>

`"changes": {"after": {..}, .. }` and `"changes": {"before": {..}, .. }` describe what changes will be made. Both objects are only contain data when *`desired config`* and *`current config`* differ. Hence this is indicates the cause for ansible reporting changed=1.

```json
  "current_config_state": {
    "api_request": {
      "method": "GET",
      "uri": "/api/data/openconfig-system:system/dns"
    }
```

`"current_config_state"` (above) describes the data received by the F5OS API for the first GET, which retrieves the *`current config`* and *`current state`*.

`"api_response"` (below) within `"current_config_state"` describes the response received from F5OS. This response also contains the `state` key which will be removed within the `"current_config"` (further below).

For confirmation, the DNS server, 9.9.9.10, is part of the configuration.

```json
    "api_response":
```

<p><details close markdown="block"><summary>expand</summary>

```json
{
  "code": 200,
  "contents": {
      "openconfig-system:dns": {
          "config": {
              "search": ["internal.example.net"]
          },
          "state": {
              "search": ["internal.example.net"]
          },
          "servers": {
              "server": [
                {"address":"8.8.8.8","config":{"address":"8.8.8.8","port":53},"state":{"port":53}},
                {"address":"9.9.9.9","config":{"address":"9.9.9.9","port":53},"state":{"port":53}},
                {"address":"9.9.9.10","config":{"address":"9.9.9.10","port":53},"state":{"port":53}}
              ]
          },
          "host-entries": {
              "host-entry": [
                {
                 "hostname":"server.internal.example.net",
                 "config":{
                  "hostname":"server.internal.example.net",
                  "ipv4-address":["192.0.2.10"]
                  },
                 "state":{
                  "hostname":"server.internal.example.net",
                  "ipv4-address":["192.0.2.10"]
                  }
                }
              ]
          }
      }
  },
  "headers": "omitted for brevity"
}
```

</details></p>

`"current_config"` (below) is the "cleaned up version" of the `"api_response"` (above).
The DNS server, 9.9.9.10, is also part of the `"current_config"`.


```json
    "current_config":
```

<p><details close markdown="block"><summary>expand</summary>

```json
{
  "openconfig-system:dns": {
    "config": {
      "search": ["internal.example.net"]
    },
    "host-entries": {
      "host-entry": [
        {
          "config": {
            "hostname": "server.internal.example.net",
            "ipv4-address": ["192.0.2.10"]
          },
          "hostname": "server.internal.example.net"
        }
      ]
    },
    "servers": {
      "server": [
        {
          "address": "8.8.8.8",
          "config": {
            "address": "8.8.8.8",
            "port": "53"
          }
        },
        {
          "address": "9.9.9.9",
          "config": {
            "address": "9.9.9.9",
            "port": "53"
          }
        },
        {
          "address": "9.9.9.10",
          "config": {
            "address": "9.9.9.10",
            "port": "53"
          }
        }
      ]
    }
  }
}
```

</details></p>

```json
    "current_state": "present"
```

`"desired_config_state"` (below) object describes the *`desired config`* and *`desired state`*.

```json
  "desired_config_state": {
    "desired_config":
```

<p><details close markdown="block"><summary>expand</summary>

```json
{
  "openconfig-system:dns": {
    "servers": {
      "server": [
        {
          "address": "9.9.9.10",
          "config": {
            "address": "9.9.9.10",
            "port": "53"
          }
        }
      ]
    }
  }
}
```

</details></p>

```json
    "desired_state": "present"
```

`"invocation"` (ansible adds this to any task) describes how the ansible module was invoked (options and data passed).

```json
  "invocation":
```

<p><details close markdown="block"><summary>expand</summary>

```json
{
  "module_args": {
    "config": {
      "openconfig-system:dns": {
        "servers": {
          "server": [
            {
              "address": "9.9.9.10",
              "config": {
                "address": "9.9.9.10",
                "port": 53
              }
            }
          ]
        }
      }
    },
    "config_query": "",
    "keys_ignore": [],
    "method": "PATCH",
    "state": "present",
    "uri": "/api/data/openconfig-system:system/dns"
  }
}
```

</details></p>

Finally `"keys_ignore"` is included by the ansible module to explicitly communicate its content.

```json
  "keys_ignore": []
```

#### Conclusions

- **DNS server already part of config**

> We can clearly see that the DNS Server is already part of the config.
> The change therefore succeeded but change identification does not work as expected.

- **desired config and current config differ**

> This is expected using `PATCH` as we do not fully declare the resource.
> With `PATCH` we only want to add to the current config.

- **changed=1 as "changes.before" and "changes.after" differ**

> "changes.before" and "changes.after" is filled when the current config and desired config does not match.

We need to make sure that we only compare the config that is relevant, e.g. we should not take `"host-entries"` and the DNS search domain(s) into account.

### Chapter Two - Attempt 2

{: .note }
> We will omit many of the responses and only focus on the relevant details for brevity.

We will attempt to solve this by using `keys_ignore`, updated playbook task below.

```yaml
- name: 'Chapter Two - Attempt 2'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
    method: 'PATCH'
    keys_ignore:
      - host-entries
      - config
    config:
      openconfig-system:dns:
        servers:
          server:
            - address: 9.9.9.10
              config:
                address: 9.9.9.10
                port: 53
  tags: ['try-2']
```

Within `"current_config_state": {"current_config": { .. } }` we find the below data.

What is missing?

- No `"host-entries"` (good!)
- No DNS search list, which was encapsulated in `"config"` (good!)
- All server entries are missing their `"config"` (**bad!**)

```json
{
    "openconfig-system:dns": {
        "servers": {
            "server": [
              {"address":"8.8.8.8"},
              {"address":"9.9.9.9"},
              {"address":"9.9.9.10"}
            ]
        }
    }
}
```

`"desired_config_state": {"desired_config": { .. } }` (below) looks like expected, this is exactly what we submit with our ansible task, just a JSON representation.

```json
{
    "openconfig-system:dns": {
        "servers": {
            "server": [
                {
                    "address": "9.9.9.10",
                    "config": {
                        "address": "9.9.9.10",
                        "port": "53"
                    }
                }
            ]
        }
    }
}
```

#### Conclusion

- **Incorrect data is removed from current config**
- **Current config still lists all DNS servers**

As we can see that the server we wanted to add is part of the current config, we need to find a way to filter the returned data in such a way that we can compare the configuration we submit (desired config) to the existing config and do not receive a change.

`keys_ignore` is great for simple cases, but in this case it is not sufficient.

Our tasks are as follows:

1. remove the `"host-entries"` key/object
2. remove the `"config"` key/object but only on the first level. This contains the DNS server search list
3. Limit the servers list to only contain the server address we have in scope

This will allow us to successfully determine if the server is already part of the current config or needs to be added.

### Chapter Three - Attempt 3

Using `config_query`, which utilizes JMESPath, actually the ansible `json_query` (`community.general.json_query`), to filter the current config. This allows us to bring the existing configuration data into the right "shape".

The below jmespath expression (`config_query`) basically searches for the DNS server address we want to add (`9.9.9.10`) in the current config and then builds the same data structure without `"config"` and `"host-entries"`.

If the current config does not contain a server with that address, the created data structure would have an empty list.

```yaml
- name: 'Attempt 3'
  vars:
    server_address: 9.9.9.10
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
    method: 'PATCH'
    config_query: |-
      "openconfig-system:dns".servers.server[?address == '{{ server_address }}'] | { "openconfig-system:dns": { servers: { server: @ } } }
    config:
      openconfig-system:dns:
        servers:
          server:
            - address: '{{ server_address }}'
              config:
                address: '{{ server_address }}'
                port: 53
```

Running the above on the existing configuration would produce the same outcome for the `"current_config"` and `"desired_config"` objects in the debug output:

```json
{
    "openconfig-system:dns": {
        "servers": {
            "server": [
                {
                    "address": "9.9.9.10",
                    "config": { "address": "9.9.9.10", "port": "53"}
                }
            ]
        }
    }
}
```

Assuming we would run the task the first time and the DNS server does not yet exist in the configuration, the `"current_config"` would look like the below, the `"server"` list is empty.
While technically other servers exist, we only care whether the server we are trying to add via `PATCH` already exists.

```json
{
    "openconfig-system:dns": {
        "servers": {
            "server": []
        }
    }
}
```

## Demo playbook

Below is a full playbook to test this yourself.

```yaml
---
- name: 'F5OS RESTCONF API troubleshooting'
  connection: httpapi
  hosts: all
  gather_facts: false
  vars:
    # f5os api prefix determination based on https port
    f5os_api_prefix: "{{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}"

  tasks:
    - name: 'Initialize Scenario'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
        config:
          openconfig-system:dns:
            config:
              search:
                - internal.example.net
            servers:
              server:
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
      tags: ['init-scenario', 'never']

    - name: 'Attempt 1'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
        method: 'PATCH'
        config:
          openconfig-system:dns:
            servers:
              server:
                - address: 9.9.9.10
                  config:
                    address: 9.9.9.10
                    port: 53
      tags: ['try-1', 'never']
      register: module_run

    - name: 'Attempt 2'
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
        method: 'PATCH'
        keys_ignore:
          - host-entries
          - config
        config:
          openconfig-system:dns:
            servers:
              server:
                - address: 9.9.9.10
                  config:
                    address: 9.9.9.10
                    port: 53
      tags: ['try-2', 'never']
      register: module_run

    - name: 'Attempt 3'
      vars:
        server_address: 9.9.9.10
      f5_ps_ansible.f5os.f5os_restconf_config:
        uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/dns'
        method: 'PATCH'
        config_query: |-
          "openconfig-system:dns".servers.server[?address == '{{ server_address }}'] | { "openconfig-system:dns": { servers: { server: @ } } }
        config:
          openconfig-system:dns:
            servers:
              server:
                - address: '{{ server_address }}'
                  config:
                    address: '{{ server_address }}'
                    port: 53
      tags: ['try-3', 'never']
      register: module_run

    - name: 'Debug data using register and ansible.builtin.debug'
      ansible.builtin.debug:
        msg:
          - "--[intial GET to fetch current config/state]---------------"
          - "api_response.code: {{ module_run.api_response.code }}"
          - "---[current_config_state]----------------------------------"
          - "current_config_state.api_response: {{ module_run.current_config_state.api_response | combine({'headers': 'omitted for brevity'}) }}"
          - "---[current_state vs. desired_state]-----------------------"
          - "current_config_state.current_state: {{ module_run.current_config_state.current_state }}"
          - "desired_config_state.desired_state: {{ module_run.desired_config_state.desired_state }}"
          - "---[current_config vs. desired_config]---------------------"
          - "current_config_state.current_config: {{ module_run.current_config_state.current_config }}"
          - "desired_config_state.desired_config: {{ module_run.desired_config_state.desired_config }}"
          - "---[ansible changed=?]-------------------------------------"
          - "changed: {{ module_run.changed }}"
          - "---[changes, derived from current_config/desired_config]--"
          - "changes.before: {{ module_run.changes.get('before') }}"
          - "changes.after: {{ module_run.changes.get('after') }}"
      tags: ['debug', 'never']
```

```shell
# init scenario
ansible-playbook <playbook> -t init-scenario

# adds the new server, changed=1
ansible-playbook <playbook> -t attempt-1 # -t debug

# server exists, changed=0 is expected but ansible reports changed=1
ansible-playbook <playbook> -t attempt-1 # -t debug

# server exists, changed=0 is expected but ansible still reports changed=1
ansible-playbook <playbook> -t attempt-2 # -t debug

# server exists, ansible finally reports changed=0
ansible-playbook <playbook> -t attempt-3 # -t debug
```

```shell
# re-init scenario
ansible-playbook <playbook> -t init-scenario

# adds the new server, changed=1
ansible-playbook <playbook> -t attempt-3 # -t debug

# server exists, ansible reports changed=0
ansible-playbook <playbook> -t attempt-3 # -t debug
```

{% endraw %}
