# Departing Employee

### add

Add a user to the departing-employee detection list. Arguments:
* `username`: A code42 username for an employee.
* `--cloud-alias` (optional): An alternative email address for another cloud service.
* `--departure-date` (optional): The date the employee is departing in format yyyy-MM-dd.
* `--notes` (optional): Notes about the employee.

Usage:

```bash
code42 departing-employee add <username> <optional-args>
```


### remove

Remove a user from the departing-employee detection list. Arguments:
* `username`: A code42 username for an employee.

Usage:

```bash
code42 departing-employee remove <username>
```

### bulk generate-template

Generate the necessary csv template needed for bulk actions. Arguments:
* `cmd`: The type of command the template with be used for. Available choices= [add, remove].

Usage:

```bash
code42 departing-employee bulk generate-template <cmd>
```

### bulk add

Bulk add users to the departing-employee detection list using a csv file. Arguments:
* `csv-file`: The path to the csv file for bulk adding users to the departing-employee detection list.

Usage:

```bash
code42 departing-employee bulk add <csv-file>
```

### bulk remove

Bulk remove users from the departing-employee detection list using a file. Arguments:
* `users-file`: A file containing a line-separated list of users to remove form the departing-employee detection
    list.

Usage:

```bash
code42 departing-employee bulk remove <users-file>
```
