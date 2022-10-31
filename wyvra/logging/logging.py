def wyvra_log(log_type="info", message=""):
    emoji = ""
    if log_type == "info":
        emoji = "\U0001f600"
    elif log_type == "prior":
        emoji = "\U0001F606"
    elif log_type == "alert":
        emoji = "\U0001F923"
    elif log_type == "debug":
        emoji = "\U0001F924"

    print("[%s%s] %s" %(log_type, emoji, message))
