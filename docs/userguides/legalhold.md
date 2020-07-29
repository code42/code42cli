# Manage legal hold custodians

Once you [create a legal hold matter in the Code42 console](https://support.code42.com/Administrator/Cloud/Configuring/Create_a_legal_hold_matter#Step_1:_Create_a_matter), you can use the Code42 CLI to add or release custodians from the matter.

Use the `legal-hold` commands to manage legal hold custodians.
 - To see a list of all the users currently in your organization, you can export a list from the [Users action menu](https://support.code42.com/Administrator/Cloud/Code42_console_reference/Users_reference#Action_menu).
 - To view a list of legal hold matters for your organization, including the matter ID, use the following command:
   `code42 legal-hold list`
 - To see a list of all the custodians currently associated with a legal hold matter, enter `code42 legal-hold show <matterID>`.


## Get CSV template

To add multiple custodians to a legal hold matter:

1. Generate a CSV template. Below is an example command that generates a template to use when bulk adding custodians to legal hold matter. Once generated, the CSV file is saved to your current working directory.
    `code42 legal-hold bulk generate-template add`

    To generate a template to use when bulk releasing custodians from a legal hold matter:

    `code42 legal-hold bulk generate-template remove`

    The CSV templates for `add` and `remove` have the same columns, but the commands generate different default filenames.

2. Use the CSV template to enter the matter ID(s) and Code42 usernames for the custodians you want to add to the matters.
To get the ID for a matter, enter `code42 legal-hold list`.
3. Save the CSV file.

## Add custodians to a legal hold matter

You can add one or more custodians to a legal hold matter using the Code42 CLI.

### Add multiple custodians
Once you have entered the matter ID and user information in the CSV file, use the `bulk add-user` command with the CSV file path to add multiple custodians at once. For example:

`code42 legal-hold bulk add-user /Users/admin/add_users_to_legal_hold.csv`

### Add a single custodian

To add a single custodian to a legal hold matter, use the following command as an example:

`code42 legal-hold add-user --matter-id 123456789123456789 --username user@example.com`

#### Options

 - `--matter-id` (required):   The identification number of the legal hold matter. To get the ID for a matter, run the command `code42 legal-hold list`.
 - `--username` (required):    The Code42 username of the custodian to add to the matter.
 - `--profile` (optional):     The profile to use to execute the command. If not specified, the default profile is used.

## Release custodians
You can [release one or more custodians](https://support.code42.com/Administrator/Cloud/Configuring/Create_a_legal_hold_matter#Release_or_reactivate_custodians) from a legal hold matter using the Code42 CLI.

### Release multiple custodians

To release multiple custodians at once:

1. Enter the matter ID(s) and Code42 usernames to the [CSV file template you generated](#get-csv-template).
2. Save the file to your current working directory.
3. Use the `bulk remove-user` command with the file path of the CSV you created. For example:
    `code42 legal-hold bulk remove-user /Users/admin/remove_users_from_legal_hold.csv`

### Release a single custodian

Use `remove-user` to release a single custodian. For example:

`code42 legal-hold remove-user --matter-id  123456789123456789 --username user@example.com`

Options are the same as `add-user` shown above.

## View matters and custodians

You can use the Code42 CLI to get a list of all the [legal hold matters](https://support.code42.com/Administrator/Cloud/Code42_console_reference/Legal_Hold_reference#All_Matters) for your organization, or get full details for a matter.

### List legal hold matters

To view a list of legal hold matters for your organization, use the following command:

`code42 legal-hold list`

This command produces the matter ID, name, description, creator, and creation date for the legal hold matters.

### View matter details

To view active custodians for a legal hold matter, enter `code42 legal-hold show` with the matter ID, for example:

`code42 legal-hold show 123456789123456789`

To view active custodians for a legal hold matter, as well as the details of the preservation policy, enter

`code42 legal-hold show <matterID> --include-policy`

To view all custodians (including inactive) for a legal hold matter, enter

`code42 legal-hold show <matterID> --include-inactive`

Learn more about the [Legal Hold](../commands/legalhold.md) commands.
