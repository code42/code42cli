import click

from code42cli.profile import get_profile


def profile_option(f):
    def callback(ctx, param, value):
        obj = ctx.ensure_object(dict)
        obj["profile"] = get_profile(value)
        return value

    return click.option("--profile", expose_value=False, callback=callback)(f)


def debug_option(f):
    def callback(ctx, param, value):
        obj = ctx.ensure_object(dict)
        obj["debug"] = value
        return value

    return click.option("-d", "--debug", is_flag=True, expose_value=False, callback=callback)(f)


def global_options(f):
    f = profile_option(f)
    f = debug_option(f)
    return f


@click.group()
@global_options
@click.pass_context
def code42(ctx):
    ctx.max_content_width = 200
