# Manage watchlist members

## List created watchlists

To list all the watchlists active in your Code42 environment, run:

```bash
code42 watchlists list
```

##  List all members of a watchlist

You can list watchlists either by their Type:

```bash
code42 watchlists list-members --watchlist-type DEPARTING_EMPLOYEE
```

or by their ID (get watchlist IDs from `code42 watchlist list` output):

```bash
code42 watchlists list-members --watchlist-id 6e6c5acc-2568-4e5f-8324-e73f2811fa7c
```

A "member" of a watchlist is any user that the watchlist alerting rules apply to. Users can be members of a watchlist
either by being explicitly added (via console or `code42 watchlists add [USER_ID|USERNAME]`), but they can also be
implicitly included based on some user profile property (like working in a specific department). To get a list of only
those "members" who have been explicitly added (and thus can be removed via the `code42 watchlists remove [USER_ID|USERNAME]`
command), add the `--only-included-users` option to `list-members`.

## Add or remove a single user from watchlist membership

A user can be added to a watchlist using either the watchlist ID or Type, just like listing watchlists, and the user
can be identified either by their user_id or their username:

```bash
code42 watchlist add --watchlist-type NEW_EMPLOYEE 9871230
```

```bash
code42 watchlist add --watchlist-id 6e6c5acc-2568-4e5f-8324-e73f2811fa7c user@example.com
```

## Bulk adding/removing users from watchlists

The bulk watchlist commands read input from a CSV file.

Like the individual commands, they can take either a user_id/username or watchlist_id/watchlist_type to identify who
to add to which watchlist. Because of this flexibility, the CSV does require a header row identifying each column.

You can generate a template CSV with the correct header values using the command:

```bash
code42 watchlists bulk generate-template [add|remove]
```

If both username and user_id are provided in the CSV row, the user_id value will take precedence. If watchlist_type and watchlist_id columns
are both provided, the watchlist_id will take precedence.

```{eval-rst}
.. note::

    For watchlists that track additional metadata for a user (e.g. the "departure date" for a user on the Departing watchlist), that data
    can be added/updated via the `code42 users bulk update-risk-profile <../commands/users.html#users-bulk-update-risk-profile>`_ command.

    You can re-use the same CSV file for both commands, just add the required risk profile columns to the CSV.

    For example, to bulk add users to multiple watchlists, with appropriate ``start_date``, ``end_date``, and ``notes`` values, create a CSV (in this example named ``watchlists.csv``) with the following::

        username,watchlist_type,start_date,end_date,notes
        user_a@example.com,DEPARTING_EMPLOYEE,,2023-10-10,
        user_b@example.com,NEW_EMPLOYEE,2022-07-04,,2022 Summer Interns

    Then run ``code42 watchlists bulk add watchlists.csv``
    followed by ``code42 users bulk update-risk-profile watchlists.csv``
```
