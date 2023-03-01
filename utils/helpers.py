import warnings


def set_custom_warning_format(msg):
    msg = "Custom Warning: " + msg

    def custom_formatwarning(*args, **kwargs):
        return str(msg) + '\n'

    warnings.formatwarning = custom_formatwarning


def issue_custom_warning(msg):
    set_custom_warning_format(msg)
    warnings.warn(msg, category=UserWarning)


issue_custom_warning("This is a custom warning message.")
