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

### Kubernetes cluster configurations
Service Account (SA)
```
kubectl create sa gitlab
```

role-deployer.yaml
```
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: default
  name: deployer
rules:
- apiGroups: ["", "extensions", "apps"]
  resources: ["services", "deployments", "replicasets", "pods", "configmap"]
  verbs: ["*"]
```

To apply this configuration:
```
kubectl apply -f role-deployer.yaml
```

rolebinding-gitlab-deployer.yaml
```
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: gitlab-deployer
  namespace: default
subjects:
- kind: User
  name: system:serviceaccount:default:gitlab
  apiGroup: ""
roleRef:
  kind: Role
  name: deployer
  apiGroup: ""
```

To apply this configuration
```
kubectl apply -f rolebinding-gitlab-deployer.yaml
```

We have to extract the token that kubernetes created for the gitlab account:
```
kubectl get sa gitlab -o yaml
kubectl get secret gitlab-token-??? -o yaml | grep token:
```

Finally, in GitLab, we define 2 variables
```
K8S_TOKEN with the token that we just extracted
K8S_SERVER with the address of the kubernetes API server
```

Kubernetes access to GitLab
To allow access from Kubernetes to the GitLab registry, navigate to Personal menu > Settings > Access Tokens and create a Personnal Access Token with the scope api.

Create a PullSecret called gitlab-token
```
kubectl create secret docker-registry gitlab-token 
  --docker-server=<gitlab.server:port>
  --docker-username=<gitlab-token-name> 
  --docker-password=<gitlab-token>
```