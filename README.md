```sh
curl -XGET "<URI>/_search?pretty" \
-H "Authorization: ApiKey <API-KEY>" \
-H 'Content-Type: application/json' -d' 
{
  "query":{
    "query_string" : {
      "query" : "query-string"
    }
  },
  "size": 1
}'
```