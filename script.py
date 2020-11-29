from collections import defaultdict

from gdc_client import get_client

client = get_client('gdc')

expand = ["demographic", "diagnoses"]
filters = {
   "op": "in",
   "content":{
       "field": "primary_site",
       "value": ["Breast"]
       }
   }

resp = client.get_cases(filters=filters, expand=expand, size=10000)

# Important fields
REQUIRED_FIELDS = {
        "demographic": [
                "updated_datetime",
                "gender",
                "race",
                #"vital_status"
                ],
        "diagnoses": [
                "ajcc_pathologic_n",
                "ajcc_pathologic_t",
                "ajcc_pathologic_m",
                #"ajcc_pathologic_stage",
                "year_of_diagnosis",
                "age_at_diagnosis"
                ],
        }
ILLEGAL_VALUES = [None, 'Not Reported']

# Custom exception
class InvalidHit(Exception):
    pass

# Filter response
hits = resp["data"]["hits"]
filtered_data = {}
for hit in hits:
    case_id = hit["case_id"]
    submitter_id = hit["submitter_id"]
    filtered_hit_data = defaultdict(dict)
    try:
        for field_1 in REQUIRED_FIELDS:
            if field_1 not in hit:
                raise InvalidHit('Did not contian {}'.format(field_1))
            for field_2 in REQUIRED_FIELDS[field_1]:
                field_hit = hit[field_1]
                # Diagnosis field is output as a list so take the first element.
                if type(field_hit) == list:
                    field_hit = field_hit[0]
                if field_2 not in field_hit:
                    raise InvalidHit('{} did not contian {}.'.format(field_1, field_2))
                if field_hit[field_2] in ILLEGAL_VALUES:
                    raise InvalidHit('{}.{} had invalid value {}.'.format(field_1,field_2,field_hit[field_2]))
                filtered_hit_data[field_1][field_2] = field_hit[field_2]
    except InvalidHit as e:
        #print(e)
        continue
    filtered_hit_data["submitter_id"] = submitter_id
    filtered_data[case_id] = filtered_hit_data

# Get Gene mutations
test_case_id = list(filtered_data.keys())[1]
test_submitter_id = filtered_data[test_case_id]["submitter_id"]

print(filtered_data[test_case_id]["submitter_id"])
ssm = client.get_ssm_occurrences(test_submitter_id)

test_ssm_id = ssm["data"]["hits"][0]["ssm_occurrence_id"]
print(test_ssm_id)
ssm_data_resp = client.get_ssm_occurrences(test_submitter_id, ssm_occurrence_id=test_ssm_id)

