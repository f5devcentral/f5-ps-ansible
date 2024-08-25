# f5_ps_ansible.f5os

This collections provides modules to configure and read resources via the RESTCONF F5OS API, it does not abstract the API too much to provide a generic ansible client for F5OS configurations. This is very useful for functionality that is not covered by the official [f5networks.f5os](https://github.com/F5Networks/f5-ansible-f5os) collection.

## Installation

```shell
ansible-galaxy collection install git@github.com:f5devcentral/f5-ps-ansible.git#ansible_collections/f5_ps_ansible/f5os,main
```

Using `requirements.yml`:

```yaml
---
- source: https://github.com/f5devcentral/f5-ps-ansible.git#ansible_collections/f5_ps_ansible/f5os
  version: main
  type: git
```

`f5_ps_ansible.f5os` is currently **NOT** available on Ansible Galaxy!


## Dependencies

This collection depends:

- `f5networks.f5os` ansible collection for the low-level API communication
- optional `deepdiff` python package, for better change diff reports
- optional `jmespath` python package, when using the `config_query` parameter of `f5os_restconf_config`

## Tests

```shell
#ansible-test units --controller docker:default --target-python 3.12
ansible-test units --controller docker:default
```

## Support, SLA and License

This is a community supported repository, please see [SUPPORT](SUPPORT.md) and [LICENSE](COPYING) for details.
