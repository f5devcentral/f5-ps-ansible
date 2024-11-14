---
title: API walkthrough - CLI
parent: f5_ps_ansible.f5os
nav_order: 6
nav_enabled: true
---

{% raw %}

## F5OS API by example

Besides reading through F5 provided examples and documentation it is very helpful to use your favorite API client (Postman, Bruno, curl, ..) and interact with it. In this section we will explore the F5OS DNS API using curl.

First, we will create a very basic set of clients using curl on bash/zsh. We assume port 443 connectivity to the F5OS Management IP and therefore also prefix the URI with /api.

{: .note }
> The F5OS API is reachable on two ports, 443 and 8888. The base path (or prefix) of the API endpoints depend on the port used. For port 443 the path begins with `/api` for port 8888 it begins with `/restconf`.

```shell
export F5OS_MGMT_IP=192.0.2.245
export F5OS_BASIC_AUTH="admin:admin"

GET() {
curl -sk -u "$F5OS_BASIC_AUTH" \
    -X GET \
    -H "Accept: application/yang-data+json" \
    https://${F5OS_MGMT_IP}:443/api${1} | jq 'del(.. | .state?)';
}

DELETE() {
curl -sk -u "$F5OS_BASIC_AUTH" \
    -X DELETE \
    -w "%{http_code}" \
    -H "Accept: application/yang-data+json" \
    https://${F5OS_MGMT_IP}:443/api${1} | jq 'del(.. | .state?)';
}

PUT() {
curl -sk -u "$F5OS_BASIC_AUTH" \
    -X PUT \
    -w "%{http_code}" \
    -H "Accept: application/yang-data+json" \
    -H "Content-Type: application/yang-data+json" \
    -d @- \
    https://${F5OS_MGMT_IP}:443/api${1} | jq 'del(.. | .state?)';
}

PATCH() {
curl -sk -u "$F5OS_BASIC_AUTH" \
    -X PATCH \
    -w "%{http_code}" \
    -H "Accept: application/yang-data+json" \
    -H "Content-Type: application/yang-data+json" \
    -d @- \
    https://${F5OS_MGMT_IP}:443/api${1} | jq 'del(.. | .state?)';
}
```

{: .note }
> `jq` is used to delete the `.state` attribute from all responses as explained in the documenation. "Raw" API responses would therefore look different to the output in the below steps.


## Step 1. Retrieve /data/openconfig-system:system/dns

```shell
GET /data/openconfig-system:system/dns
```

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
        "host-entry": [{"hostname": "server.internal.example.net", "config": {"hostname": "server.internal.example.net", "ipv4-address":["192.0.2.10"]}}]
    }
  }
}
```

{: .note }
> To keep the documentation concise the GET to the modified resource will not be repeated after every modification, the reader is advised to perform this action nevertheless for a better understanding of the API.

## Step 2. Add additional DNS resolvers

Let's add additional DNS resolvers, 8.8.4.4, 9.9.9.10, 9.9.9.11 and 149.112.112.112.

We now have three methods:

1. Declaring the whole /dns resource. This is declarative but also absolute, we assume full authority about the resource.
2. Declaring a single server, working on an item-by-item basis. This is declarative as well but *per-item*, hence allows shared control over the configuration.
3. Using the PATCH method

We'll use all three methods.

```shell
cat <<END_OF_REQUEST_DATA | PUT /data/openconfig-system:system/dns
{
  "openconfig-system:dns": {
    "config": {
      "search": ["internal.example.net"]
    },
    "servers": {
        "server": [
            {"address": "8.8.4.4", "config":{"address": "8.8.4.4", "port": 53}},
            {"address": "8.8.8.8", "config":{"address": "8.8.8.8", "port": 53}},
            {"address": "9.9.9.9", "config":{"address": "9.9.9.9", "port": 53}}
        ]
    },
    "host-entries": {
        "host-entry": [{"hostname": "server.internal.example.net", "config": {"hostname": "server.internal.example.net", "ipv4-address":["192.0.2.10"]}}]
    }
  }
}
END_OF_REQUEST_DATA
```

```shell
204
```

The PUT method only returned a http status code (204), no payload/content typically returned when an operation succeeds.
When we issue a GET we expect the DNS resolver/server to be part of the list. We actually expect the DNS resource to look exactly like the payload we sent.
If we would have omitted `"host-entries"` or `"config": {"search": [..]}`, those configurations would have been deleted as per our "desired configuration" (declarative!).

## Step 3. Item-level resource declaration

Now we are going to declare a single item, but how do we do that?
First let's retrieve a single item.

```shell
GET /data/openconfig-system:system/dns/servers/server=9.9.9.9
```

```json
{
  "openconfig-system:server": [
    {
      "address": "9.9.9.9",
      "config": {
        "address": "9.9.9.9",
        "port": 53
      }
    }
  ]
}
```

The correct URI can be retrieved from the API response of the first request we sent. `"servers": { "server": [ .. ] }` where `..` are the actual items. The items are addressable via their value in the `"address"` key. The name of the key does not really matter here, many other resources have other names for the keys like `"name"` or `"id"`. Usually there is a single key right next to the `"config"` object, hence it can be easily identified.

Now we add a new item (DNS resolution server):

```shell
cat <<END_OF_REQUEST_DATA | PUT /data/openconfig-system:system/dns/servers/server=9.9.9.10
{
  "openconfig-system:server": [
    {
      "address": "9.9.9.10",
      "config": {
        "address": "9.9.9.10",
        "port": 53
      }
    }
  ]
}
END_OF_REQUEST_DATA
```

```shell
201
```

Once again there is no return data. But this time the http status code is 201 (Created). If we would submit exactly the same request again, we would receive a http status code 204 (No Content). Usually 201 indicates a new item has been created while 204 indicates "no change".

{: .important }
> It is not recommended to base a logic decision solely on the response code as not all API endpoints and methods of interaction cause the same behavior. Therefore it is advised to retrieve the resource again if checks are supposed to be implemented.

## Step 4. Using PATCH

Next up is the `PATCH` method. We will target the /dns resource (`/data/openconfig-system:system/dns`).

With PATCH we only need to specify what configuration should be modified or added. We can omit other configuration items (eg. other servers) or sections like `"host-entries"` and `"config": {"search": [..]}`.

```shell
cat <<END_OF_REQUEST_DATA | PATCH /data/openconfig-system:system/dns
{
  "openconfig-system:dns": {
    "servers": {
        "server": [
            {"address": "9.9.9.11", "config":{"address": "9.9.9.11", "port": 53}}
        ]
    }
  }
}
END_OF_REQUEST_DATA
```

```shell
204
```

Again we only receive an http status code (204), repeated calls will also only yield a 204.


## Step 5. PUT on dns/servers API resource

Finally the last DNS resolver we will add using PUT/fully declarative but we will tighten our scope to the `dns/servers` resource. This allows us to omit `"host-entries"` and `"config": {"search": [..]}` safely. Ultimately we are only interested in defining the servers at this point.

Again we will first send a GET, this will provide us with the right format although we could probably guess this by now.

```shell
 GET /data/openconfig-system:system/dns/servers
```

```json
{
    "openconfig-system:servers": {
        "server":[
            {"address":"8.8.4.4","config":{"address":"8.8.4.4","port":53}},
            {"address":"8.8.8.8","config":{"address":"8.8.8.8","port":53}},
            {"address":"9.9.9.9","config":{"address":"9.9.9.9","port":53}},
            {"address":"9.9.9.10","config":{"address":"9.9.9.10","port":53}},
            {"address":"9.9.9.11","config":{"address":"9.9.9.11","port":53}}
        ]
    }
}
```

```shell
cat <<END_OF_REQUEST_DATA | PUT /data/openconfig-system:system/dns/servers
{
    "openconfig-system:servers": {
        "server":[
            {"address":"8.8.4.4","config":{"address":"8.8.4.4","port":53}},
            {"address":"8.8.8.8","config":{"address":"8.8.8.8","port":53}},
            {"address":"9.9.9.9","config":{"address":"9.9.9.9","port":53}},
            {"address":"9.9.9.10","config":{"address":"9.9.9.10","port":53}},
            {"address":"9.9.9.11","config":{"address":"9.9.9.11","port":53}},
            {"address":"149.112.112.112","config":{"address":"149.112.112.112","port":53}}
        ]
    }
}
END_OF_REQUEST_DATA
```

```shell
204
```

Retrieving `/data/openconfig-system:system/dns` now would show that the servers are exactly those defined above and `"host-entries"` and `"config": {"search": [..]}` have not been modified by our operation.

## Step 6. Remove configuration resources declaratively (on Group-level)

While mentioned already, we now demonstrate how to remove configuration items/resources using the declarative PUT method as well as DELETE.

```shell
cat <<END_OF_REQUEST_DATA | PUT /data/openconfig-system:system/dns/servers
{
    "openconfig-system:servers": {
        "server":[
            {"address":"8.8.8.8","config":{"address":"8.8.8.8","port":53}},
            {"address":"9.9.9.9","config":{"address":"9.9.9.9","port":53}},
            {"address":"9.9.9.10","config":{"address":"9.9.9.10","port":53}},
            {"address":"9.9.9.11","config":{"address":"9.9.9.11","port":53}}
        ]
    }
}
END_OF_REQUEST_DATA
```

```shell
204
```

8.8.4.4 and 149.112.112.112 have been removed now / the list of servers is exactly as defined by our PUT call above.

## Step 7. Remove item-level resources
Removal of individual items is doable using the DELETE method, the URI is the same as for item-based resource declaration:

```shell
DELETE /data/openconfig-system:system/dns/servers/server=8.8.8.8
```

```shell
204
```

Executing the DELETE again or executing a GET on this resource

```shell
DELETE /data/openconfig-system:system/dns/servers/server=8.8.8.8
# or GET /data/openconfig-system:system/dns/servers/server=8.8.8.8
```

will yield an error message

```json
{
  "ietf-restconf:errors": {
    "error": [
      {
        "error-type": "application",
        "error-tag": "invalid-value",
        "error-message": "uri keypath not found"
      }
    ]
  }
}
```

along with a `404` http status code.


## Congratulations!

Congratulations, you completed your first F5OS RESTCONF API journey!

If you wonder how that helps you creating an ansible playbook, have a look at the next section!

{% endraw %}