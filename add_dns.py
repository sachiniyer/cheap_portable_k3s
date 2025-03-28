"""
Ensure that records match nginx.conf.

1. Get all domains from nginx.conf
2. Get all domains from Route53
3. Delete all domains from Route53 that are not in nginx.conf
4. Add all domains from nginx.conf that are not in Route53
5. Add *.sachiniyer.com to Route53 with private IP
"""

import boto3
import dotenv
import os

dotenv.load_dotenv()

public_ip = os.environ["PUBLIC_IP"]
private_ip = os.environ["PRIVATE_IP"]
hosted_zone = os.environ["HOSTED_ZONE"]
client = boto3.client("route53")
dry_run = False
wildcard_domain = "\\052.sachiniyer.com."
exception_domains = ["api.sachiniyer.com.", wildcard_domain]


def get_domains():
    """
    Get domains from nginx.conf.

    Returns:
        domains: list of domains from nginx.conf
        exception_domains: list of domains to not delete
    """
    with open("nginx.conf", "r") as f:
        nginx_conf = f.readlines()

    domains = []
    reading = False
    for line in nginx_conf:
        if "map $ssl_preread_server_name" in line:
            reading = True
            continue
        if reading:
            if "}" in line:
                break
            domains.append(line.split()[0])

    domains = [f"{domain}." for domain in domains]
    return domains


def delete_records(records):
    """
    Delete records from Route53 that are not in nginx.conf.

    Returns:
        route53domains: list of domains in Route53 already
    """
    route53domains = []
    for record in records["ResourceRecordSets"]:
        # TODO: Check whether the record value is also correct
        if record["Name"] not in keep_domains and record["Type"] == "A":
            print(f"Deleting {record['Name']}")
            if not dry_run:
                _ = client.change_resource_record_sets(
                    HostedZoneId=hosted_zone,
                    ChangeBatch={
                        "Comment": "string",
                        "Changes": [
                            {
                                "Action": "DELETE",
                                "ResourceRecordSet": {
                                    "Name": record["Name"],
                                    "Type": record["Type"],
                                    "TTL": record["TTL"],
                                    "ResourceRecords": [
                                        {
                                            "Value": record["ResourceRecords"][0][
                                                "Value"
                                            ]  # noqa E501
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                )

        elif record["Type"] == "A":
            route53domains.append(record["Name"])
    return route53domains


def add_records(add_domains):
    """
    Add records to Route53 that are in nginx.conf but not in Route53.

    Args:
        add_domains: list of domains to add to Route53
    """
    for domain in add_domains:
        print(f"Adding {domain}")
        if not dry_run:
            _ = client.change_resource_record_sets(
                HostedZoneId=hosted_zone,
                ChangeBatch={
                    "Comment": "string",
                    "Changes": [
                        {
                            "Action": "CREATE",
                            "ResourceRecordSet": {
                                "Name": domain,
                                "Type": "A",
                                "TTL": 300,
                                "ResourceRecords": [
                                    {"Value": public_ip},
                                ],
                            },
                        },
                    ],
                },
            )


def set_wildcard(records):
    """
    Set wildcard domain to private IP.

    Args:
        records: list of records in Route53
    """
    wildcard_exists = False
    for record in records["ResourceRecordSets"]:
        if record["Name"] == wildcard_domain:
            if not (
                record["Type"] == "A"
                and record["ResourceRecords"][0]["Value"] == private_ip
            ):  # noqa E501
                if not dry_run:
                    print("Wildcard domain does not match private IP")
                    _ = client.change_resource_record_sets(
                        HostedZoneId=hosted_zone,
                        ChangeBatch={
                            "Comment": "string",
                            "Changes": [
                                {
                                    "Action": "DELETE",
                                    "ResourceRecordSet": {
                                        "Name": record["Name"],
                                        "Type": record["Type"],
                                        "TTL": record["TTL"],
                                        "ResourceRecords": [
                                            {
                                                "Value": record["ResourceRecords"][0][
                                                    "Value"
                                                ]  # noqa E501
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                    )
                wildcard_exists = False
            else:
                wildcard_exists = True

    if not wildcard_exists:
        print("Wildcard domain does not exist")
        if not dry_run:
            _ = client.change_resource_record_sets(
                HostedZoneId=hosted_zone,
                ChangeBatch={
                    "Comment": "string",
                    "Changes": [
                        {
                            "Action": "CREATE",
                            "ResourceRecordSet": {
                                "Name": "*.sachiniyer.com.",
                                "Type": "A",
                                "TTL": 300,
                                "ResourceRecords": [
                                    {"Value": private_ip},
                                ],
                            },
                        },
                    ],
                },
            )


records = client.list_resource_record_sets(
    HostedZoneId=hosted_zone,
)

domains = get_domains()
keep_domains = domains + exception_domains
route53domains = delete_records(records)
add_domains = set(domains) - set(route53domains)
add_records(add_domains)
set_wildcard(records)

print("Done")
