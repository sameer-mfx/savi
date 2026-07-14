def savi_param_bool(env, key, default=False):
    value = env["ir.config_parameter"].sudo().get_param(
        "savi_message_automation.%s" % key,
        "1" if default else "0",
    )
    return str(value).lower() in ("1", "true", "yes", "on")


def savi_param_int(env, key, default=0):
    value = env["ir.config_parameter"].sudo().get_param(
        "savi_message_automation.%s" % key,
        str(default),
    )
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
