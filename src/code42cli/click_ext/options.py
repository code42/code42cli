import click


def incompatible_with(incompatible_opts):
    """Factory for creating custom `click.Option` subclasses that enforce incompatibility with the
    option strings passed to this function.
    """

    if isinstance(incompatible_opts, str):
        incompatible_opts = [incompatible_opts]

    class IncompatibleOption(click.Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            # if None it means we're in autocomplete mode and don't want to validate
            if ctx.obj is not None:
                found_incompatible = ", ".join(
                    [
                        "--{}".format(opt.replace("_", "-"))
                        for opt in opts
                        if opt in incompatible_opts
                    ]
                )
                if self.name in opts and found_incompatible:
                    name = self.name.replace("_", "-")
                    raise click.BadOptionUsage(
                        option_name=self.name,
                        message="--{} can't be used with: {}".format(
                            name, found_incompatible
                        ),
                    )
            return super().handle_parse_result(ctx, opts, args)

    return IncompatibleOption
