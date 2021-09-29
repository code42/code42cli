# Manage Users

## Manage User Roles

## Update a User

## Reactivate or Deactivate a User

## Assign an Organization

## Bulk Commands

### Get CSV Template

The following command will generate a CSV template to either update users' data, or move users between organizations.  The csv file will be saved to the current working directory.
```bash
code42 trusted-activities bulk generate-template [update|move]
```

Each of the CSV templates can then be filled out and used with their respective bulk command. 
```bash
code42 trusted-activities bulk [update|move|reactivate|deactivate] Users/my_user/bulk-command.csv
```

A CSV with a single `username` column is used for the `reactivate` and `deactivate` bulk commands.  They are not available as options for `generate-template`.

### update
### move
### reactivate
### deactivate
