```json
GET sysflow/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "range": { "@timestamp": {"gte": "now-10s"} }
        },
        {
         "term": { "event.category": { "value": "network" } }
        },
        {
          "term": { "destination.ip": { "value": "192.168.200.3" } }
        },
        {
          "term": { "destination.port": { "value": "22"} }
        }
      ]
    }
  }
}
```
