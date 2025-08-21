import logging

logger = logging.getLogger(__name__)

def normalize_course_data(data):
    # Convert install_availability to boolean
    if "install_availability" in data:
        val = str(data["install_availability"]).lower()
        if val == "true":
            data["install_availability"] = True
        elif val == "false":
            data["install_availability"] = False
        elif isinstance(data["install_availability"], bool):
            pass
        else:
            return data, "Invalid value for install_availability"
    else:
        data["install_availability"] = False

    logger.info(f"Normalize install_availability")

    # Convert numeric fields
    try:
        if "course_duration" in data:
            data["course_duration"] = int(data["course_duration"])
            logger.info(f"Normalize course_duration")

        if "course_fee" in data:
            data["course_fee"] = float(data["course_fee"])
            logger.info(f"Normalize course_fee")

    except ValueError:
        return data, "Invalid number format for course_duration or course_fee"

    return data, None
