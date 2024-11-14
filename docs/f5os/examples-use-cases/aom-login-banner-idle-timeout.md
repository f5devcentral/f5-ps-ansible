---
title: Configure AOM Login Banner and Idle Timeout
parent: Examples / Use-Cases
nav_order: 1
nav_enabled: true
---
{% raw %}

# Configure AOM Login Banner and Idle Timeout

### Checking the current settings

```yaml
- name: 'Read AOM resource: f5-system-aom:aom'
  f5_ps_ansible.f5os.f5os_restconf_get:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/f5-system-aom:aom'
  register: aom_get

- name: 'Display AOM resource: f5-system-aom:aom'
  ansible.builtin.debug:
    var: aom_get.api_response.contents
```

```json
{
  "f5-system-aom:aom": {
    "config": {
        "ssh-session-banner": "With great power comes great responsibility!\n-- Spider-man's grandpa",
        "ssh-session-idle-timeout": 600
    },
    "state": {
        "ssh-session-banner": "With great power comes great responsibility!\n-- Spider-man's grandpa",
        "ssh-session-idle-timeout": 600,
        "ssh-username": ""
    }
  }
}
```

### Checking the current settings using /config

```yaml
- name: 'Read AOM resource: f5-system-aom:aom/config'
  f5_ps_ansible.f5os.f5os_restconf_get:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/f5-system-aom:aom/config'
  register: aom_get

- name: 'Display AOM resource: f5-system-aom:aom'
  ansible.builtin.debug:
    var: aom_get.api_response.contents
```

```json
{
    "f5-system-aom:config": {
        "ssh-session-banner": "With great power come great resp..",
        "ssh-session-idle-timeout": 600
    }
}
```

### Validating which configuration options exist for this resource


f5sh / rseries cli (admin):

```shell
my-rSeries # show running-config system aom config
Possible completions:
  ipv4                       Configure AOM IPv4 interface.
  ipv6                       Configure AOM IPv6 interface.
  ssh-session-banner         A banner or message displayed when the ssh session is connected.
  ssh-session-idle-timeout   Idle timeout for session in seconds.
```

Available options are:

- `ipv4`
- `ipv6`
- `ssh-session-banner`
- `ssh-session-idle-timeout`

If we can only claim authority over `ssh-session-idle-timeout` we need to use PATCH and specify `keys_ignore` with the rest of the options.

{: .note }
> Note the exact resource URI and desired `config:`

```yaml
- name: 'AOM Idle Timeout'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/f5-system-aom:aom'
    method: PATCH
    config:
      f5-system-aom:aom:
        config:
          ssh-session-idle-timeout: 245
    keys_ignore:
      - ssh-session-banner
      - ipv4
      - ipv6
```

If we can only claim authority over `ssh-session-banner`, we need to use PATCH and specify `keys_ignore` with the rest of the options.

{: .note }
> Note the exact resource URI and desired `config:`
> It differs to the previous task definition but essentially performs the same task.

```yaml
- name: 'AOM Login Banner'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/f5-system-aom:aom/config'  # note the /config
    method: PATCH
    config:
      f5-system-aom:config:  # note the difference to AOM Idle Timeout
        ssh-session-banner: |-
          With great power comes great responsibility!
          -- Spider-man's grandpa
    keys_ignore:
      - ssh-session-idle-timeout
      - ipv4
      - ipv6
```

If we can claim full authority over the `aom` resource, we can declare the configuration in full.

{: .note }
> ipv4/ipv6 is not specified, for practical use this would be configured as well.

```yaml
- name: 'AOM Idle Timeout & Login Banner'
  f5_ps_ansible.f5os.f5os_restconf_config:
    uri: '{{ f5os_api_prefix }}/data/openconfig-system:system/f5-system-aom:aom'
    config:
      f5-system-aom:aom:
        config:
          ssh-session-idle-timeout: 245
          ssh-session-banner: |-
            With great power comes great responsibility!
            -- Spider-man's grandpa
    keys_ignore:
      - ssh-session-banner
```

{% endraw %}