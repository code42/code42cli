# High Risk Employee

## add

Add a user to the high-risk-employee detection list. 

Arguments:
* `username`: A code42 username for an employee.
* `--cloud-alias` (optional): An alternative email address for another cloud service.
* `-risk-tag` (optional): Risk tags associated with the user.  Options include: [FLIGHT_RISK, HIGH_IMPACT_EMPLOYEE, 
    ELEVATED_ACCESS_PRIVILEGES, PERFORMANCE_CONCERNS, SUSPICIOUS_SYSTEM_ACTIVITY, POOR_SECURITY_PRACTICES, 
    CONTRACT_EMPLOYEE].
* `--notes` (optional): Notes about the employee.

Usage:
```bash
code42 high-risk-employee add <username> <optional-args>
```

## remove

Remove a user from the high-risk-employee detection list.

 Arguments:
* `username`: A code42 username for an employee.

Usage:
```bash
code42 high-risk-employee remove <username>
```

## add-risk-tags

Associates risk tags with a user.

Arguments:
* `--username`, `-u`:  A code42 username for an employee.
* `--tag`:  Risk tags associated with the employee. 
    Options include: [FLIGHT_RISK, HIGH_IMPACT_EMPLOYEE, ELEVATED_ACCESS_PRIVILEGES, PERFORMANCE_CONCERNS, 
    SUSPICIOUS_SYSTEM_ACTIVITY, POOR_SECURITY_PRACTICES, CONTRACT_EMPLOYEE].
    
Usage:
```bash
code42 high-risk-employee add-risk-tags --username <username> --tag <risk-tags>
```

## remove-risk-tags

Disassociates risk tags from a user.

Arguments:
* `--username`, `-u`:  A code42 username for an employee.
* `--tag`:  Risk tags associated with the employee. 
    Options include: [FLIGHT_RISK, HIGH_IMPACT_EMPLOYEE, ELEVATED_ACCESS_PRIVILEGES, PERFORMANCE_CONCERNS, 
    SUSPICIOUS_SYSTEM_ACTIVITY, POOR_SECURITY_PRACTICES, CONTRACT_EMPLOYEE].
    
Usage:
```bash
code42 high-risk-employee remove-risk-tags --username <username> --tag <risk-tags>
```

## bulk generate-template

Generate the necessary csv template for bulk actions.

Arguments:
* `cmd`: The type of command the template with be used for. Available choices= [add, remove].

Usage:
```bash
code42 high-risk-employee bulk generate-template <cmd>
```

## bulk add

Bulk add users to the high-risk-employee detection list using a csv file.

Arguments:
* `csv-file`: The path to the csv file for bulk adding users to the high-risk-employee detection list.

Usage:
```bash
code42 high-risk-employee bulk add <csv-file>
```

## bulk remove

Bulk remove users from the high-risk-employee detection list using a file.

Arguments:
* `users-file`: A file containing a line-separated list of users to remove form the high-risk-employee detection
    list.

Usage:
```bash
code42 high-risk-employee bulk remove <users-file>
```
