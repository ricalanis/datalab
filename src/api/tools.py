def format_response(longitude, latitude, mode, head, list_points):
    response = {}
    response["longitude"]= longitude
    response["latitude"]= latitude
    response["mode"] = mode
    response["head"] = head
    response["points"] = list_points
    return response
