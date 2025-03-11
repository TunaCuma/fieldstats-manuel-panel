import numpy as np


def reverse_transform_point(point):
    """
    Reverse transforms a 2D point using one of two homography matrices.

    For points where the x-coordinate is greater than 347, it subtracts 347 and reads
    the homography matrix from "al1_homography_matrix.txt". Otherwise, it uses the matrix from
    "al2_homography_matrix.txt". Then, it computes the inverse and applies it.

    Parameters:
        point (list or tuple): The [x, y] coordinate to reverse transform.

    Returns:
        isRight (bool): True if the original x was > 347, else False.
        new_point (list): The reverse-transformed [x, y] coordinate.
    """
    x, y = point
    isRight = x > 347
    # Select the appropriate homography matrix file based on the x-coordinate.
    H = np.loadtxt(
        "al1_homography_matrix.txt" if isRight else "al2_homography_matrix.txt"
    )
    # If the point is from the right side, adjust x by subtracting 347.
    x_adjusted = x - 347 if isRight else x
    # Compute the inverse of the homography matrix.
    H_inv = np.linalg.inv(H)
    # Convert the adjusted point to homogeneous coordinates.
    homogeneous_point = np.array([x_adjusted, y, 1])
    # Apply the inverse transformation.
    orig_point = H_inv.dot(homogeneous_point)
    # Normalize to convert back to Cartesian coordinates.
    orig_point /= orig_point[2]
    return isRight, [float(orig_point[0]), float(orig_point[1])]


# Example usage:
# if __name__ == "__main__":
#     with open("test.json", "r") as f:
#         tracking_data = json.load(f)

#     updated_tracking_data = format_tracking_data(tracking_data)

#     with open("tracking_data_reversed.json", "w") as f:
#         json.dump(updated_tracking_data, f, indent=4)

#     print("Tracking data formatted and updated with reverse-transformed centers and src property.")
