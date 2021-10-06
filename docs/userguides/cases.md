# Add and Manage Cases

To create a new case, only providing the name is required.  Other attributes are optional and can be provided through the available flags.

The following command creates a case with the subject and assignee users indicated by their respective UIDs.
```bash
code42 cases create My-Case --subject 123 --assignee 456 --description "Sample case"
```

## Update a Case

To further update or view the details of your case, you'll need the case's unique number, which is assigned upon creation.  To get this number, you can use the `list` command to view all cases, with optional filter values.

To print to the console all open cases created in the last 30 days:
```bash
code42 cases list --begin-create-time 30d --status OPEN
```

#### Example Output
Example output for a single case in JSON format.
```json
{
    "number": 42,
    "name": "My-Case",
    "createdAt": "2021-9-17T18:29:53.375136Z",
    "updatedAt": "2021-9-17T18:29:53.375136Z",
    "description": "Sample case",
    "findings": "",
    "subject": "123",
    "subjectUsername": "sean.cassidy@example.com",
    "status": "OPEN",
    "assignee": "456",
    "assigneeUsername": "elvis.presley@example.com",
    "createdByUserUid": "789",
    "createdByUsername": "andy.warhol@example.com",
    "lastModifiedByUserUid": "789",
    "lastModifiedByUsername": "andy.warhol@example.com"
}
```

Once you've identified your case's number, you can view further details on the case, or update its attributes.

The following command will print all details of your case.
```bash
code42 cases show 42
```

If you've finished your investigation and you'd like to close your case, you can update the status of the case.  Similarly, other attributes of the case can be updated using the optional flags.
```bash
code42 cases update 42 --status CLOSED
```

## Get CSV Template

The following command will generate a CSV template to either add or remove file events from multiple cases at once.  The csv file will be saved to the current working directory.
```bash
code42 cases file-events bulk generate-template [add|remove]
```

You can then fill out and use each of the CSV templates with their respective bulk commands.
```bash
code42 cases file-events bulk [add|remove] bulk-command.csv
```

For example, to associate one or more file exposure events to one or more cases at once:

1. Generate a CSV template. Below is the command for generating a template to add file events to cases. Once generated, the CSV file is saved to your current working directory.

```bash
code42 cases bulk generate-template add
```

2. Use the CSV template to enter the case and file event information.
   The `number` and `event_id` fields are required. The `number` refers to the identifying case number to add the events, and the `event_id` refers to the ID of the file exposure event to associate with the case.

3. Save the CSV file.

## Manage File Exposure Events Associated with a Case

The following example command can be used to view all the file exposure events currently associated with a case, indicated here by case number `42`.
```bash
code42 cases file-events list 42
```

Use the `file-events add` command to associate a single file event, referred to by event ID, to a case.

Below is an example command to associate some event with ID `event_abc` with case number `42`.
```bash
code42 cases file-events add 42 event_abc
```

To associate multiple file events with one or more cases at once, enter the case and file event information into the `file-events add` CSV file template, then use the `bulk add` command with the CSV file path. For example:
```bash
code42 cases file-events bulk add my_new_cases.csv
```

Similarly, the `remove` and `bulk remove` commands can be used to remove a file event from a case.

## Export Case Details

You can use the CLI to export the details of a case into a PDF.

The following example command will download the details from case number `42` and save a PDF with the name `42_case_summary.pdf` to the provided path.  If a path is not provided, it will be saved to the current working directory.

```bash
code42 cases export 42 --path Users/my_user/cases/
```

Learn more about the [Managing Cases](../commands/cases.md).
