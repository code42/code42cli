# Ingest file event data or alerts into a SIEM tool

This guide provides instructions on using the CLI to ingest Code42 file event data or alerts 
into a security information and event management (SIEM) tool like LogRhythm, Sumo Logic, or IBM QRadar.

## Considerations

To ingest file events or alerts into a SIEM tool using the Code42 command-line interface, the Code42 user account running the integration
must be assigned roles that provide the necessary permissions.

## Before you begin

First install and configure the Code42 CLI following the instructions in
[Getting Started](gettingstarted.md).

## Run queries
You can get file events in either a JSON or CEF format for use by your SIEM tool. Alerts data is available in JSON format. You can query the data as a
scheduled job or run ad-hoc queries. Learn more about [searching](../commands/securitydata.md) using the CLI.

### Run a query as a scheduled job

Use your favorite scheduling tool, such as cron or Windows Task Scheduler, to run a query on a regular basis. Specify
the profile to use by including `--profile`. An example using `netcat` to forward only the new file event data since the previous request to an external syslog server:
```bash
code42 security-data search --profile profile1 -c syslog_sender | nc syslog.example.com 514
```

An example to send to the syslog server only the new alerts that meet the filter criteria since the previous request: 
```bash
code42 alerts send-to "https://syslog.example.com:514" -p UDP --profile profile1 --rule-name “Source code exfiltration” --state OPEN -i
```

As a best practice, use a separate profile when executing a scheduled task. Using separate profiles can help prevent accidental updates to your stored checkpoints, for example, by adding `--use-checkpoint` to adhoc queries.

### Run an ad-hoc query

Examples of ad-hoc queries you can run are as follows.

Print file events since March 5 for a user in raw JSON format:
```bash
code42 security-data search -f RAW-JSON -b 2020-03-05 --c42-username 'sean.cassidy@example.com'
```

Print file events since March 5 where a file was synced to a cloud service:
```bash
code42 security-data search -t  CloudStorage -b 2020-03-05
```

Write to a text file the file events in raw JSON format where a file was read by browser or other app for a user since
March 5:
```bash
code42 security-data search -f RAW-JSON -b 2020-03-05 -t ApplicationRead --c42-username 'sean.cassidy@example.com' > /Users/sangita.maskey/Downloads/c42cli_output.txt
```

Print alerts since May 5 where a file's cloud share permissions changed: 
```bash
code42 alerts print -b 2020-05-05 --rule-type FedCloudSharePermissions
``` 

Example output for a single file exposure event (in default JSON format):

```json
{
    "eventId": "0_c4b5e830-824a-40a3-a6d9-345664cfbb33_942704829036142720_944009394534374185_342",
    "eventType": "CREATED",
    "eventTimestamp": "2020-03-05T14:45:49.662Z",
    "insertionTimestamp": "2020-03-05T15:10:47.930Z",
    "filePath": "C:/Users/sean.cassidy/Google Drive/",
    "fileName": "1582938269_Longfellow_Cloud_Arch_Redesign.drawio",
    "fileType": "FILE",
    "fileCategory": "DOCUMENT",
    "fileSize": 6025,
    "fileOwner": "Administrators",
    "md5Checksum": "9ab754c9133afbf2f70d5fe64cde1110",
    "sha256Checksum": "8c6ba142065373ae5277ecf9f0f68ab8f9360f42a82eb1dec2e1816d93d6b1b7",
    "createTimestamp": "2020-03-05T14:29:33.455Z",
    "modifyTimestamp": "2020-02-29T01:04:31Z",
    "deviceUserName": "sean.cassidy@example.com",
    "osHostName": "LAPTOP-091",
    "domainName": "192.168.65.129",
    "publicIpAddress": "71.34.10.80",
    "privateIpAddresses": [
        "fe80:0:0:0:8d61:ec3f:9e32:2efc%eth2",
        "192.168.65.129",
        "0:0:0:0:0:0:0:1",
        "127.0.0.1"
    ],
    "deviceUid": "942704829036142720",
    "userUid": "887050325252344565",
    "source": "Endpoint",
    "exposure": [
        "CloudStorage"
    ],
    "syncDestination": "GoogleBackupAndSync"
}
```
Example output for a single alert (in default JSON format):

```json
{"type$": "ALERT_DETAILS", 
"tenantId": "c4b5e830-824a-40a3-a6d9-345664cfbb33", 
"type": "FED_CLOUD_SHARE_PERMISSIONS", 
"name": "Cloud Share", 
"description": "Alert Rule for data exfiltration via Cloud Share", 
"actor": "leland.stewart@example.com", 
"target": "N/A", 
"severity": "HIGH", 
"ruleId": "408eb1ae-587e-421a-9444-f75d5399eacb", 
"ruleSource": "Alerting", 
"id": "7d936d0d-e783-4b24-817d-f19f625e0965", 
"createdAt": "2020-05-22T09:47:33.8863230Z", 
"state": "OPEN", 
"observations": [{"type$": "OBSERVATION", 
"id": "4bc378e6-bfbd-40f0-9572-6ed605ea9f6c", 
"observedAt": "2020-05-22T09:40:00.0000000Z", 
"type": "FedCloudSharePermissions", 
"data": {"type$": "OBSERVED_CLOUD_SHARE_ACTIVITY", 
"id": "4bc378e6-bfbd-40f0-9572-6ed605ea9f6c", 
"sources": ["GoogleDrive"], 
"exposureTypes": ["PublicLinkShare"], 
"firstActivityAt": "2020-05-22T09:40:00.0000000Z", 
"lastActivityAt": "2020-05-22T09:45:00.0000000Z", 
"fileCount": 1, 
"totalFileSize": 6025, 
"fileCategories": [{"type$": "OBSERVED_FILE_CATEGORY", "category": "Document", "fileCount": 1, "totalFileSize": 6025, "isSignificant": false}], 
"files": [{"type$": "OBSERVED_FILE", "eventId": "1hHdK6Qe6hez4vNCtS-UimDf-sbaFd-D7_3_baac33d0-a1d3-4e0a-9957-25632819eda7", "name": "1590140395_Longfellow_Cloud_Arch_Redesign.drawio", "category": "Document", "size": 6025}], 
"outsideTrustedDomainsEmailsCount": 0, "outsideTrustedDomainsTotalDomainCount": 0, "outsideTrustedDomainsTotalDomainCountTruncated": false}}]}
```

## CEF Mapping

The following tables map the file event data from the Code42 CLI to common event format (CEF).

### Attribute mapping

The table below maps JSON fields, CEF fields, and [Forensic Search fields](https://code42.com/r/support/forensic-search-fields)
to one another.

```eval_rst

+----------------------------+---------------------------------+----------------------------------------+
| JSON field                 | CEF field                       | Forensic Search field                  |
+============================+=================================+========================================+
| actor                      | suser                           | Actor                                  |
+----------------------------+---------------------------------+----------------------------------------+
| cloudDriveId               | aid                             | n/a                                    |
+----------------------------+---------------------------------+----------------------------------------+
| createTimestamp            | fileCreateTime                  | File Created Date                      |
+----------------------------+---------------------------------+----------------------------------------+
| deviceUid                  | deviceExternalId                | n/a                                    |
+----------------------------+---------------------------------+----------------------------------------+
| deviceUserName             | suser                           | Username (Code42)                      |
+----------------------------+---------------------------------+----------------------------------------+
| domainName                 | dvchost                         | Fully Qualified Domain Name            |
+----------------------------+---------------------------------+----------------------------------------+
| eventId                    | externalID                      | n/a                                    |
+----------------------------+---------------------------------+----------------------------------------+
| eventTimestamp             | end                             | Date Observed                          |
+----------------------------+---------------------------------+----------------------------------------+
| exposure                   | reason                          | Exposure Type                          |
+----------------------------+---------------------------------+----------------------------------------+
| fileCategory               | fileType                        | File Category                          |
+----------------------------+---------------------------------+----------------------------------------+
| fileName                   | fname                           | Filename                               |
+----------------------------+---------------------------------+----------------------------------------+
| filePath                   | filePath                        | File Path                              |
+----------------------------+---------------------------------+----------------------------------------+
| fileSize                   | fsize                           | File Size                              |
+----------------------------+---------------------------------+----------------------------------------+
| insertionTimestamp         | rt                              | n/a                                    |
+----------------------------+---------------------------------+----------------------------------------+
| md5Checksum                | fileHash                        | MD5 Hash                               |
+----------------------------+---------------------------------+----------------------------------------+
| modifyTimesamp             | fileModificationTime            | File Modified Date                     |
+----------------------------+---------------------------------+----------------------------------------+
| osHostName                 | shost                           | Hostname                               |
+----------------------------+---------------------------------+----------------------------------------+
| processName                | sproc                           | Executable Name (Browser or Other App) |
+----------------------------+---------------------------------+----------------------------------------+
| processOwner               | spriv                           | Process User (Browser or Other App)    |
+----------------------------+---------------------------------+----------------------------------------+
| publiclpAddress            | src                             | IP Address (public)                    |
+----------------------------+---------------------------------+----------------------------------------+
| removableMediaBusType      | cs1,                            | Device Bus Type (Removable Media)      |
|                            | Code42AEDRemovableMediaBusType  |                                        |
+----------------------------+---------------------------------+----------------------------------------+
| removableMediaCapacity     | cn1,                            | Device Capacity (Removable Media)      |
|                            | Code42AEDRemovableMediaCapacity |                                        |
+----------------------------+---------------------------------+----------------------------------------+
| removableMediaName         | cs3,                            | Device Media Name (Removable Media)    |
|                            | Code42AEDRemovableMediaName     |                                        |
+----------------------------+---------------------------------+----------------------------------------+
| removableMediaSerialNumber | cs4                             | Device Serial Number (Removable Media) |
+----------------------------+---------------------------------+----------------------------------------+
| removableMediaVendor       | cs2,                            | Device Vendor (Removable Media)        |
|                            | Code42AEDRemovableMediaVendor   |                                        |
+----------------------------+---------------------------------+----------------------------------------+
| sharedWith                 | duser                           | Shared With                            |
+----------------------------+---------------------------------+----------------------------------------+
| syncDestination            | destinationServiceName          | Sync Destination (Cloud)               |
+----------------------------+---------------------------------+----------------------------------------+
| url                        | filePath                        | URL                                    |
+----------------------------+---------------------------------+----------------------------------------+
| userUid                    | suid                            | n/a                                    |
+----------------------------+---------------------------------+----------------------------------------+
| windowTitle                | requestClientApplication        | Tab/Window Title                       |
+----------------------------+---------------------------------+----------------------------------------+
| tabUrl                     | request                         | Tab URL                                |
+----------------------------+---------------------------------+----------------------------------------+
| emailSender                | suser                           | Sender                                 |
+----------------------------+---------------------------------+----------------------------------------+
| emailRecipients            | duser                           | Recipients                             |
+----------------------------+---------------------------------+----------------------------------------+
```

### Event mapping

See the table below to map file events to CEF signature IDs.

```eval_rst

+--------------------+-----------+
| Exfiltration event | CEF field |
+====================+===========+
| CREATED            | C42200    |
+--------------------+-----------+
| MODIFIED           | C42201    |
+--------------------+-----------+
| DELETED            | C42202    |
+--------------------+-----------+
| READ_BY_APP        | C42203    |
+--------------------+-----------+
| EMAILED            | C42204    |
+--------------------+-----------+
```
