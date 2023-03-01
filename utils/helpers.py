import warnings


def set_custom_warning_format(msg):
    msg = "Warning: " + msg

    def custom_formatwarning(*args, **kwargs):
        return str(msg) + '\n'

    warnings.formatwarning = custom_formatwarning


def issue_custom_warning(msg):
    set_custom_warning_format(msg)
    warnings.warn(msg, category=UserWarning)


if __name__ == "__main__":
    issue_custom_warning("This is a custom warning message.")
