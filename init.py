#!/usr/bin/python3

import os
import time

import requests
import urllib3

urllib3.disable_warnings()

API_URL = os.environ['API_URL']
API_SECRET = os.environ['API_SECRET']

service_order = 0


def create_group(name, service_creators):
    global service_order

    response = requests.post(
        "{}/groups".format(API_URL),
        headers={
            'Authorization': API_SECRET,
            'Content-Type': 'application/json;charset=UTF-8'
        },
        json={'name': name, 'public': True},
        verify=False
    )

    print(response)
    group_id = response.json()['id']
    for service_creator in service_creators:
        service_order += 1
        service_creator(group_id, service_order)


def http(order, group_id, name, permalink, url, status=200, port=80):
    requests.post(
        "{}/services".format(API_URL),
        headers={
            'Authorization': API_SECRET,
            'Content-Type': 'application/json;charset=UTF-8'
        },
        json={
            "name": name,
            "type": "http",
            "domain": url,
            "group_id": group_id,
            "method": "GET",
            "post_data": "",
            "headers": "",
            "expected": "",
            "expected_status": status,
            "port": port,
            "check_interval": 60,
            "timeout": 15,
            "permalink": permalink,
            "order": order,
            "verify_ssl": True,
            "grpc_health_check": False,
            "redirect": True,
            "allow_notifications": True,
            "notify_all_changes": False,
            "notify_after": 2,
            "public": True,
            "tls_cert": "",
            "tls_cert_key": "",
            "tls_cert_root": ""
        },
        verify=False
    )


def tcp(order, group, name, permalink, host, port):
    requests.post(
        "{}/services".format(API_URL),
        headers={
            'Authorization': API_SECRET,
            'Content-Type': 'application/json;charset=UTF-8'
        },
        json={
            "name": name,
            "type": "tcp",
            "domain": host,
            "group_id": group,
            "method": "GET",
            "post_data": "",
            "headers": "",
            "expected": "",
            "expected_status": 200,
            "port": port,
            "check_interval": 60,
            "timeout": 15,
            "permalink": permalink,
            "order": order,
            "verify_ssl": True,
            "grpc_health_check": False,
            "redirect": True,
            "allow_notifications": True,
            "notify_all_changes": False,
            "notify_after": 2,
            "public": True,
            "tls_cert": "",
            "tls_cert_key": "",
            "tls_cert_root": ""
        },
        verify=False
    )


def wait_for_api():
    tries = 10
    sleep = 6

    print("Waiting for API at {} to come online".format(API_URL))
    while tries >= 0:
        # noinspection PyBroadException
        try:
            response = requests.get("{}/health".format(API_URL), timeout=10, verify=False)
            if response.status_code == 200:
                return
        except Exception:
            if tries == 0:
                raise Exception("API at {} did not respond in time".format(API_URL))

        time.sleep(sleep)
        tries -= 1


wait_for_api()

create_group("Critical Services", [
    lambda group_id, order: tcp(order, group_id, "Lobby", "lobby", "lobby.faforever.com", 8001),
    lambda group_id, order: http(order, group_id, "API", "api", "https://api.faforever.com"),
    lambda group_id, order: tcp(order, group_id, "IRC", "irc", "irc.faforever.com", 6697),
    lambda group_id, order: http(order, group_id, "Vault", "vault", "https://content.faforever.com", 403),
    lambda group_id, order: http(order, group_id, "Authentication", "auth", "https://hydra.faforever.com/health/ready"),
])

create_group("Other Services", [
    lambda group_id, order: http(order, group_id, "Website", "website", "https://www.faforever.com"),
    lambda group_id, order: tcp(order, group_id, "Live Replay", "live-replay", "lobby.faforever.com", 15000),
    lambda group_id, order: http(order, group_id, "Forum", "forum", "https://forum.faforever.com"),
    lambda group_id, order: http(order, group_id, "Wiki", "wiki", "https://wiki.faforever.com"),
    lambda group_id, order: http(order, group_id, "Unit DB", "unit-db", "https://unitdb.faforever.com"),
])
