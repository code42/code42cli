# Integrating with SIEM Tools

The Code42 command-line interface (CLI) tool offers a way to interact with your Code42 environment without using the 
Code42 console or making API calls directly. This article provides instructions on using the CLI to extract Code42 data 
for use in a security information and event management (SIEM) tool like LogRhythm, Sumo Logic, or IBM QRadar. 

You can also use the Code42 CLI to bulk-add or remove users from the High Risk Employees list or Departing Employees 
list. For more information, see Manage detection list users with the Code42 command-line interface. 

## Considerations

To integrate with a SIEM tool using the Code42 command-line interface, the Code42 user account running the integration 
must be assigned roles that provide the necessary permissions. We recommend you assign the roles in our use case for 
managing a security application integrated with Code42.

## Before you begin

To integrate Code42 with a SIEM tool, you must first install and configure the Code42 CLI following the instructions in 
[Getting Started](gettingstarted.md) the Code42 command-line interface. 

## Commands and query parameters 
You can get security events in either a JSON or CEF format for use by your SIEM tool. You can query the data as a 
scheduled job or run ad-hoc queries. Learn more about [searching](../commands/securitydata.md) using the CLI.

## Run a query as a scheduled job

Use your favorite scheduling tool, such as cron or Windows Task Scheduler, to run a query on a regular basis. Specify 
the profile to use by including `--profile`. An example using `netcat` to forward results to an external syslog server:  

```bash
code42 security-data search --profile profile1 -c syslog_sender | nc syslog.example.com 514 
```

Note that it is best practice to use a separate profile when executing a scheduled task. This way, it is harder to 
accidentally mess up your stored checkpoints by running `--use-checkpoint` in adhoc queries.

This query will send to the syslog server only the new security event data since the previous request.

## Run an ad-hoc query

Examples of ad-hoc queries you can run are as follows. 

Print security data since March 5 for a user in raw JSON format:

```bash
code42 security-data search -f RAW-JSON -b 2020-03-05 --c42-username 'sean.cassidy@example.com'
```

Print security events since March 5 where a file was synced to a cloud service: 
```bash
code42 security-data search -t  CloudStorage -b 2020-03-05 
```

Write to a text file security events in raw JSON format where a file was read by browser or other app for a user since 
March 5: 
```bash
code42 security-data search -f RAW-JSON -b 2020-03-05 -t ApplicationRead --c42-username 'sean.cassidy@example.com' > /Users/sangita.maskey/Downloads/c42cli_output.txt
```

Example output for a single exposure event (in default JSON format): 

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

## CEF Mapping

The following tables map the data from the Code42 CLI to common event format (CEF).

### Attribute mapping

The table below maps JSON fields, CEF fields, and [Forensic Search fields](https://support.code42.com/Administrator/Cloud/Administration_console_reference/Forensic_Search_reference_guide) 
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

See the table below to map exfiltration events to CEF signature IDs. 

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

