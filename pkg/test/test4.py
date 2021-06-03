from retry import retry

from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# class Fen(object):
    
    
#     tri = 0
#     def __init__(self, appNs=None):
#         self.appNs = appNs
#         self.test_max_delay = retry(exceptions=Exception,max_delay=2*appNs,tries=appNs, delay=appNs/2, backoff=0)(self.test_max_delay)

#     print("Tri :", tri)
#     def test_max_delay(self):
#         try:
#             print("Tess")
#             val = 1/0
#         except Exception as e:
#             raise Exception
        
#         return None

# fen = Fen(3)

# err = fen.test_max_delay()
# print("Err", err)
