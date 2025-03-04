import tracker  # Your tracker module with the update function


def update_data(data):
    """
    Processes the tracking update using the provided JSON-like dictionary.

    Parameters:
        data (dict): Dictionary expected to contain 'coord_id' and 'frame_id'.

    Returns:
        dict: A dictionary containing the results of the update, or an error message.
    """
    if not data:
        return {"error": "No JSON payload provided"}

    # Extract the expected fields
    coord_id = data.get("coord_id")
    frame_id = data.get("frame_id")

    # Validate the received data
    if coord_id is None or frame_id is None:
        return {"error": "Missing one or more required parameters: coord_id, frame_id"}

    try:
        # Call the update function from tracker. It is assumed to return:
        # (lost_frame_id, lost_ids, tracking_response)
        lost_frame_id, lost_ids, tracking_response = tracker.update(frame_id, coord_id)
    except Exception as e:
        return {"error": str(e)}

    # If tracking_response has a get_json method, use it to extract the JSON
    # content.
    if hasattr(tracking_response, "get_json"):
        tracks = tracking_response.get_json()
    else:
        tracks = tracking_response

    # Return the combined response as a dictionary
    return {"lost_frame_id": lost_frame_id, "tracks": tracks, "lost_ids": lost_ids}
