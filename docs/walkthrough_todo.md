    uri: "{{ default('/restconf' if ansible_httpapi_port == '8888' else '/api') }}/data/openconfig-system:system/dns/config/search"


GET() { curl -sk -X GET -u admin:admin -H "Accept: application/yang-data+json" https://10.170.9.37:443/api$1 | jq; }

GET /data/openconfig-system:system/dns
{
  "openconfig-system:dns": {
    "config": {
      "search": [
        "example.net",
        "internal.example.com"
      ]
    },
    "state": {
      "search": [
        "example.net",
        "internal.example.com"
      ]
    },
    "servers": {
      "server": [
        {
          "address": "8.8.8.8",
          "config": {
            "address": "8.8.8.8",
            "port": 53
          },
          "state": {
            "port": 53
          }
        },
        {
          "address": "9.9.9.9",
          "config": {
            "address": "9.9.9.9",
            "port": 53
          },
          "state": {
            "port": 53
          }
        }
      ]
    },
    "host-entries": {
      "host-entry": [
        {
          "hostname": "my-webserver.example.net",
          "config": {
            "hostname": "my-webserver.example.net",
            "alias": [
              "www1.example.net",
              "www2.example.net"
            ],
            "ipv4-address": [
              "192.0.2.4",
              "192.0.2.8"
            ],
            "ipv6-address": [
              "db9:deeb::9"
            ]
          },
          "state": {
            "hostname": "my-webserver.example.net",
            "alias": [
              "www1.example.net",
              "www2.example.net"
            ],
            "ipv4-address": [
              "192.0.2.4",
              "192.0.2.8"
            ],
            "ipv6-address": [
              "db9:deeb::9"
            ]
          }
        },
        {
          "hostname": "simons-host",
          "config": {
            "hostname": "simons-host",
            "ipv4-address": [
              "192.0.2.4"
            ]
          },
          "state": {
            "hostname": "simons-host",
            "ipv4-address": [
              "192.0.2.4"
            ]
          }
        }
      ]
    }
  }
}



GET /data/openconfig-system:system/dns/config
{
  "openconfig-system:config": {
    "search": [
      "example.net",
      "internal.example.com"
    ]
  }
}


GET() { curl -sk -X GET -u admin:admin -H "Accept: application/yang-data+json" https://10.170.9.37:443/api$1 | | jq 'del(.. | .state?)'; }

GET /data/openconfig-system:system/dns/servers
{
  "openconfig-system:servers": {
    "server": [
      {
        "address": "8.8.8.8",
        "config": {
          "address": "8.8.8.8",
          "port": 53
        }
      },
      {
        "address": "9.9.9.9",
        "config": {
          "address": "9.9.9.9",
          "port": 53
        }
      }
    ]
  }
}


GET /data/openconfig-system:system/dns/servers/server=9.9.9.9
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

DELETE() { curl -sk -X DELETE -w "%{http_code}" -u admin:admin -H "Accept: application/yang-data+json" https://10.170.9.37:443/api$1; }



DELETE /data/openconfig-system:system/dns/servers/server=9.9.9.9
204

DELETE /data/openconfig-system:system/dns/servers/server=9.9.9.9
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
404

GET /data/openconfig-system:system/dns/servers/server
{
  "openconfig-system:server": [
    {
      "address": "8.8.8.8",
      "config": {
        "address": "8.8.8.8",
        "port": 53
      }
    }
  ]
}


GET /data/openconfig-system:system/dns/servers
{
  "openconfig-system:servers": {
    "server": [
      {
        "address": "8.8.8.8",
        "config": {
          "address": "8.8.8.8",
          "port": 53
        }
      }
    ]
  }
}
 

GET /data/openconfig-system:system/dns/servers/server
{
  "openconfig-system:server": [
    {
      "address": "8.8.8.8",
      "config": {
        "address": "8.8.8.8",
        "port": 53
      }
    },
    {
      "address": "9.9.9.9",
      "config": {
        "address": "9.9.9.9",
        "port": 53
      }
    }
  ]
}

GET /data/openconfig-system:system/dns/host-entries
{
  "openconfig-system:host-entries": {
    "host-entry": [
      {
        "hostname": "my-webserver.example.net",
        "config": {
          "hostname": "my-webserver.example.net",
          "alias": [
            "www1.example.net",
            "www2.example.net"
          ],
          "ipv4-address": [
            "192.0.2.4",
            "192.0.2.8"
          ],
          "ipv6-address": [
            "db9:deeb::9"
          ]
        }
      },
      {
        "hostname": "simons-host",
        "config": {
          "hostname": "simons-host",
          "ipv4-address": [
            "192.0.2.5"
          ]
        }
      }
    ]
  }
}

DELETE /data/openconfig-system:system/dns/servers/server=9.9.9.9
204

GET /data/openconfig-system:system/dns/servers/server=9.9.9.9
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


DELETE /data/openconfig-system:system/dns/servers/server=9.9.9.9
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
404
