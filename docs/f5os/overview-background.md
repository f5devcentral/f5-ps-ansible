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
3. declare specific items of a resources individually (e.g. individual VLANs of a Tenant)

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

In RESTCONF, the terms "resource", "item", "element", and "object" are often used somewhat interchangeably, but they generally refer to different aspects of the data model and API structure.

- Resource: A resource is the fundamental concept in RESTCONF. It refers to any addressable entity within the API that can be accessed, manipulated, or queried. Resources are typically defined by YANG data models and are represented by URIs. They can include configuration data (`config`), state data (`state`), operations, or even the API root itself.

- Item: Often refers to a specific instance of a resource, especially in the context of list entries.

- Element: Refers to a specific part of the YANG data model, such as a container or list.

- Object: While not a formal RESTCONF term, "object" is sometimes used to describe a collection of related data, similar to how it's used JSON or similar data structures.

Example:

- The API root ("`/api/data`") is a resource.
- A specific configuration container (e.g., "`api/data/openconfig-system:system`") is both a *resource* and an *element*.
- An individual list entry within that container could be considered an *item* or an *object* (e.g. "`api/data/openconfig-system:system/dns/servers/server=9.9.9.9`").

## Important notes

- Many API endpoints will have a `config` element as well as a `state` element (on the same leaf level), but some endpoints/resources miss the `state` element.

- Depending on how resources are addressed, config and state is prefixed with the resource name, for example `resource-name:config` or `resource-name:state`.

- For the purposes of this ansible module the `state` element is not relevant and is therefore filtered from the API responses, this includes `*:state` as well.

- Numbers are often not expressed as a string in JSON/by the RESTCONF API. This is why all numbers are treated as strings by this ansible collection.

- Depending on the HTTP method and endpoint, the HTTP status code can indicate whether a new resource is created (201 for PUT) or just updated (204). Errors are typically indicated by 4xx (404 -> resource/config object not found) or even 5xx HTTP status codes.
