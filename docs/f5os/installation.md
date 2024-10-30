---
title: Installation
parent: f5_ps_ansible.f5os
nav_order: 4
nav_enabled: true
---

## Installation

```shell
ansible-galaxy collection install \
  git@github.com:f5devcentral/f5-ps-ansible.git#ansible_collections/f5_ps_ansible/f5os,main
```

Using `requirements.yml`:

```yaml
---
# main branch, always the latest code
- source: https://github.com/f5devcentral/f5-ps-ansible.git#ansible_collections/f5_ps_ansible/f5os
  version: main
  type: git

# specific release, version 1.1.0 in this example
#- source: https://github.com/f5devcentral/f5-ps-ansible.git#ansible_collections/f5_ps_ansible/f5os
#  version: main
#  type: 1.1.0
```

```shell
ansible-galaxy install -r requirements.yml
```

{: .note }
> `f5_ps_ansible.f5os` is currently **NOT** available on Ansible Galaxy!

## Dependencies

This collection depends:

- `f5networks.f5os` ansible collection for the low-level API communication
- optional `deepdiff` python package, for better change diff reports
- optional `jmespath` python package, when using the `config_query` parameter of `f5os_restconf_config`
