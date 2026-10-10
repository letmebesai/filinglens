"""Live check against SEC EDGAR. Needs FILINGLENS_SEC_USER_AGENT set.

Run:  python scripts/smoke_test.py
"""

from filinglens.sec.client import SecClient

APPLE_CIK = 320193

with SecClient() as client:
    data = client.submissions(APPLE_CIK)

recent = data["filings"]["recent"]["accessionNumber"]
print(f"{data['name']}: {len(recent)} recent filings. First accession: {recent[0]}")
