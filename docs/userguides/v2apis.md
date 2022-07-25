# V2 File Events

```{eval-rst}
.. warning:: V1 file events, saved searches, and queries are **deprecated**.
```

For details on the updated File Event Model, see the V2 File Events API documentation on the [Developer Portal](https://developer.code42.com/api/#tag/File-Events).

V1 file event APIs were marked deprecated in May 2022 and will be no longer be supported after May 2023.

Use the `--use-v2-file-events` flag with the `code42 profile create` or `code42 profile update` commands to enable your code42 CLI profile to use the latest V2 file event data model.

Use `code42 profile show` to check the status of this setting on your profile:
```bash
% code42 profile update --use-v2-file-events

% code42 profile show

test-user-profile:
        * username = test-user@code42.com
        * authority url = https://console.core-int.cloud.code42.com
        * ignore-ssl-errors = False
        * use-v2-file-events = True

```

For details on setting up a profile, see the [profile configuration user guide](./profile.md).

Enabling this setting will use the V2 data model for querying searches and saved searches with all `code security-data` commands.
The response shape for these events has changed from V1 and contains various field remappings, renamings, additions and removals.  Column names will also be different when using the `Table` format for outputting events.

### V2 File Event Data Example ###

Below is an example of the new file event data model:

```json
{
    "@timestamp": "2022-07-14T16:53:06.112Z",
    "event": {
        "id": "0_c4e43418-07d9-4a9f-a138-29f39a124d33_1068825680073059134_1068826271084047166_1_EPS",
        "inserted": "2022-07-14T16:57:00.913917Z",
        "action": "application-read",
        "observer": "Endpoint",
        "shareType": [],
        "ingested": "2022-07-14T16:55:04.723Z",
        "relatedEvents": []
    },
    "user": {
        "email": "engineer@example.com",
        "id": "1068824450489230065",
        "deviceUid": "1068825680073059134"
    },
    "file": {
        "name": "cat.jpg",
        "directory": "C:/Users/John Doe/Downloads/",
        "category": "Spreadsheet",
        "mimeTypeByBytes": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "categoryByBytes": "Spreadsheet",
        "mimeTypeByExtension": "image/jpeg",
        "categoryByExtension": "Image",
        "sizeInBytes": 4748,
        "owner": "John Doe",
        "created": "2022-07-14T16:51:06.186Z",
        "modified": "2022-07-14T16:51:07.419Z",
        "hash": {
            "md5": "8872dfa1c181b823d2c00675ae5926fd",
            "sha256": "14d749cce008711b4ad1381d84374539560340622f0e8b9eb2fe3bba77ddbd64",
            "md5Error": null,
            "sha256Error": null
        },
        "id": null,
        "url": null,
        "directoryId": [],
        "cloudDriveId": null,
        "classifications": []
    },
    "report": {
        "id": null,
        "name": null,
        "description": null,
        "headers": [],
        "count": null,
        "type": null
    },
    "source": {
        "category": "Device",
        "name": "DESKTOP-1",
        "domain": "192.168.00.000",
        "ip": "50.237.00.00",
        "privateIp": [
            "192.168.00.000",
            "127.0.0.1"
        ],
        "operatingSystem": "Windows 10",
        "email": {
            "sender": null,
            "from": null
        },
        "removableMedia": {
            "vendor": null,
            "name": null,
            "serialNumber": null,
            "capacity": null,
            "busType": null,
            "mediaName": null,
            "volumeName": [],
            "partitionId": []
        },
        "tabs": [],
        "domains": []
    },
    "destination": {
        "category": "Cloud Storage",
        "name": "Dropbox",
        "user": {
            "email": []
        },
        "ip": null,
        "privateIp": [],
        "operatingSystem": null,
        "printJobName": null,
        "printerName": null,
        "printedFilesBackupPath": null,
        "removableMedia": {
            "vendor": null,
            "name": null,
            "serialNumber": null,
            "capacity": null,
            "busType": null,
            "mediaName": null,
            "volumeName": [],
            "partitionId": []
        },
        "email": {
            "recipients": null,
            "subject": null
        },
        "tabs": [
            {
                "title": "Files - Dropbox and 1 more page - Profile 1 - Microsoft​ Edge",
                "url": "https://www.dropbox.com/home",
                "titleError": null,
                "urlError": null
            }
        ],
        "accountName": null,
        "accountType": null,
        "domains": [
            "dropbox.com"
        ]
    },
    "process": {
        "executable": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "owner": "John doe"
    },
    "risk": {
        "score": 17,
        "severity": "CRITICAL",
        "indicators": [
            {
                "name": "First use of destination",
                "weight": 3
            },
            {
                "name": "File mismatch",
                "weight": 9
            },
            {
                "name": "Spreadsheet",
                "weight": 0
            },
            {
                "name": "Remote",
                "weight": 0
            },
            {
                "name": "Dropbox upload",
                "weight": 5
            }
        ],
        "trusted": false,
        "trustReason": null
    }
}

```
