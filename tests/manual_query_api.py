from app.data_cloud_client import run_query

sql = """
SELECT
    "Id__c",
    "Name__c",
    "Phone__c"
FROM "Account_Home__dll"
LIMIT 10
"""

result = run_query(sql)

print(result)