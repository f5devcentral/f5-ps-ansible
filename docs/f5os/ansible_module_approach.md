---
title: Ansible module approach
parent: f5_ps_ansible.f5os
nav_order: 7
nav_enabled: true
---

{% raw %}

# Ansible module approach

`f5os_restconf_config` uses the `f5networks.f5os` collection to connect to the F5OS system, which uses the ansible `httpapi` connection type.

`f5os_restconf_config` is not just a simple API client, it performs multiple tasks in the background to simplify the interaction with the F5OS RESTCONF API while allowing a maximum of flexibility.

## f5os_restconf_config arguments

```yaml
vars:
    f5os_api_prefix: {{ '/restconf' if ansible_httpapi_port == '8888' else '/api' }}
f5_ps_ansible.f5os.f5os_restconf_config:
    uri: "{{ f5os_api_prefix }}/data/api-endpoint/of/resource"
    method: PUT # PUT or PATCH, PUT is the default
    config: .. # The desired config of the resource
    state: present # present or absent, present is the default
    keys_ignore: [] # a list of keys in the desired config
                    # and current config to ignore recursively(!)
    config_query: # a JMESPath query to apply to the current configuration
                  # before it is compared to the desired configuration
```

## GET before PUT/PATCH

The first action is to issue a HTTP `GET` to retrieve the *`current config`* (actual resource configuration) and *`current state`* (resource currently present or absent?) from the F5OS system.

**If the resource does not exist, the *`current state`* is `absent`.**

Depending on the *`desired state`* (defined as `state: present/absent`, `present` is the default), a configuration action would be taken or not.

If the *`desired state`* is `absent` and matches the *`current state`*, then no action would be taken and ansible would indicate that with no change made ("ok").

Otherwise if the *`desired state`* is `present` and the *`current state`* is `absent` the *`desired config`* (indicated in the `config:` specification of the `f5os_restconf_config` module) will be submitted using the desired `method` (PUT is the default, PATCH is another option).

## *`desired config`* and *`current config`*

However if both, *`current state`* and *`desired state`* are `present`, the *`current config`* will be compared to the *`desired config`* to identify if a change is necessary.

To compare both configs requires:

1. to ignore the `state` (and `*:state`) elements (keys/properties in json) in the *`current config`*
2. take care of type differences, such as numbers represented as strings (this differs across resource types and API endpoints)
3. format bool values properly ("true", true, True, ..) in the *`desired config`* (this is a common issue with Ansible/python booleans and YAML)
4. to reduce the **scope of comparison** to relevant config as the *`desired config`* can be a subset of the *`current config`*

Therefore `f5os_restconf_config` will perform the following actions:

1. remove the `state` (and `*:state`) keys from the *`current config`* JSON data structure (actually python dict)
2. convert all numeric values to strings
3. format bool values properly
4. see below

## Scope of comparison: *`desired config`* vs. *`current config`*

Sometimes a config operation is performed on a subset of the overall configuration element or resource, this is specifically true when using the `PATCH` method. PATCH allows partial updates to a subset of settings.

This, however, is a problem when trying to determine if the *`desired config`* differs from the *`current config`* as both are not equal.

`f5os_restconf_config` therefore offers two options to deal with this challenge:

- **`keys_ignore`**
- **`config_query`**

### Option `keys_ignore`

`keys_ignore` expects a list of keys which will be removed from the *`current config`* **recursively** before comparing it the *`desired config`*.

Assuming `keys_ignore: ["other"]` the below data would be equal:

```yaml
# desired config
config:
  element:
    setting-one: 1
```

```yaml
# current config
config:
  element:
    setting-one: 1
    other:  # will be ignored
      key: value
```

### Option `config_query`

`config_query` applies the specified JMESPath query to the *`current config`*.

{: .note}
The jmespath python module is required for this option to work.

For the previous example, the below jmespath query would achieve the same as `keys_ignore: ["other"]`:

```yaml
f5_ps_ansible.f5os.f5os_restconf_config:
  uri: ..
  config: ..
  config_query: |-
    {config: {element: {"setting-one": config.element."setting-one"}}}
```

### Summary

Depending on the complexity of the data returned by the API either `keys_ignore` or `config_query` should be used.


{% endraw %}
