---
title: Overview & Background
parent: f5_ps_ansible.f5os
nav_order: 2
nav_enabled: true
---

## Overview

`f5_ps_ansible.f5os` aims to fill the gap between raw API interactions and the F5 provided ansible collection for F5OS.

It therefore is somewhere between `ansible.builtin.uri` and `f5networks.f5os` in terms of complexity and features.

**Compared to `f5networks.f5os`:**

`f5_ps_ansible.f5os` provides more flexibility and let's you, the implementor, decide whether you want to:

1. fully declare a configuration 'in hole' of a resource
2. only patch some of its settings
3. declare specific items of the resources individually

In addition it supports almost all F5OS API endpoints.

{: .new-title }
> Tip!
> 
> When combining `f5networks.f5os` and `f5_ps_ansible.f5os` most configuration scenarios should be achievable.

**Compared to `ansible.builtin.uri` or any other raw HTTPS client:**

`f5_ps_ansible.f5os` provides you with:

- diff and check mode
- typing is taken care of (many numeric values are considered a string)
- idempotency is implemented
- comparison of desired and current configuration is in place

The below guide should get you started.

## Background

In general the F5OS API is based on RESTCONF, which is the "REST API version of NETCONF". Both are based on the same YANG models, which describe the configuration, it's attributes and also 'state' of the resource. 'state' does not only refer to the configuration state but furthermore to state information of the relevant resource (eg. interface statistics).

The F5OS API leverages RESTCONF, a RESTful interface for NETCONF, to manage network configurations. Both protocols use so called YANG models to define the structure and semantics of configuration and state data. In this context, 'config' refers to the desired configuration of a resource, while 'state' provides operational status information such as interface statistics.

RESTCONF supports both XML and JSON data formats. This ansible collection uses JSON exclusively and focuses on 'config' data, filtering out 'state' information to streamline configuration management.

## Important notes

- Many API endpoints will have a `config` object as well as a `state` object, but some miss the `state` object.

- Depending on how resources are addressed, config and state is prefixed with the resource name, for example `resource-name:config` or `resource-name:state`.

- For the purposes of this ansible module the `state` object is not relevant and is therefore filtered from the API responses, this includes `*:state` as well.

- Numbers are often not expressed as a string in JSON/by the RESTCONF API. This is why all numbers are treated as strings by this ansible collection.
