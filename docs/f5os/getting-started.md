---
title: Getting Started
parent: f5_ps_ansible.f5os
nav_order: 5
nav_enabled: true
---

To get started we will run through examples looking at the API.

First a few basics about the F5OS API and its behaviors.

## Declarative configuration

The F5OS API is primarily declarative, meaning that it allows users to define the desired state of the system without specifying the exact steps to achieve that state. However, the scope of "declarativeness" can be chosen based on individual requirements.

In certain areas, such as managing interfaces, F5OS allows for iterating over multiple resources of the same type. This flexibility enables users to choose whether to declare the entire list of resources or each individual item separately.

## Imperative configuration

Some tasks require multiple API interactions even though one might have expected to only require one. Unfortunately at the time of writing there is no atomic operation mode available to combine those interactions into a single action, requiring an implementor to take care of each step and order of execution.

For example when configuring F5OS network connectivity one might expect to configure LAGs, Interface speed, LACP and LLDP. These are distinct API interactions, though, making the whole task imperative.

Often times the order of execution also matters and is different for creation and deletion, like in the example above.

Fortunately, Ansible provides a solution for this scenario, by using the ansible "idempotent state pattern" 'state': 'present' and 'state': 'absent' as parameters to the specific ansible module and coupling the required API interactions with blocks and/or roles (or additional abstractions) to achieve the desired configuration state and ensure the resource is created or deleted in the specific order.

## API Scope: Group-level vs. Item-level Configuration

Many times the F5OS RESTCONF API provides flexibility in terms of the scope of configuration, allowing users to interact with resources at different levels of granularity. This hierarchical approach, similar to a directory structure, enables implementors to manage configurations efficiently based on their specific needs.

### Group-level resource configuration

At the broader level, the API allows users to manage entire groups of related resources. This approach is particularly useful when you need to configure or modify multiple items of the same type simultaneously.

For example:

- Declaring all VLANs at once (absolute)
- Declaring all DNS resolution Servers at once (absolute)

Group-level configuration is efficient for bulk operations and maintaining consistency across similar resources. It reduces the number of API calls required and simplifies the management of large-scale configurations and supports the use of a single source of truth.

### Item-level resource configuration

In many cases the F5OS RESTCONF API also supports granular control over individual items within a "group of resources".

Specifically when multiple sources of truth exist, e.g. F5OS devices are build/bootstrapped automatically via ansible and another orchestrator will take care of use-case specific configuration, this mode is very effective.

For example: Ansible is used to build/provision and maintain base settings and configurations for F5OS. At the same time an orchestrator will need to add/delete/modify VLANs. If one system would assume control over the whole VLAN configuration both systems would be in conflict. By utilizing an item-level configuration, the decision of "scope" and "ownership", hence the source of truth, can be defined *per-item*.
