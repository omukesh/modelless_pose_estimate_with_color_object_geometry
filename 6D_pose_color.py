import pyrealsense2 as rs
import numpy as np
import cv2
import math

# ✅ Real camera intrinsics from ChArUco calibration
camera_matrix = np.array([
    [232.85084894, 0.0, 331.6771862],
    [0.0, 229.492061, 244.54631673],
    [0.0, 0.0, 1.0]
], dtype=np.float64)

# ✅ Real distortion coefficients
dist_coeffs = np.array([[-0.05227928, 0.13806631, 0.00202788, 0.00154673, -0.12901652]], dtype=np.float64)

# Object dimensions in meters
cube_size = 0.05
screwdriver_height = 0.10
screwdriver_radius = 0.009


def rotationMatrixToEulerAngles(R):
    sy = math.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0
    return np.degrees([x, y, z])


def get_pose(object_points, image_points):
    success, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)
    if success:
        rotation_matrix, _ = cv2.Rodrigues(rvec)
        euler_angles = rotationMatrixToEulerAngles(rotation_matrix)
        return tvec.ravel(), euler_angles, rvec, tvec
    return None, None, None, None


def draw_pose(frame, image_points, rvec, tvec, label, t, r):
    axis = np.float32([[0.02, 0, 0], [0, 0.02, 0], [0, 0, 0.02]]).reshape(-1, 3)
    imgpts, _ = cv2.projectPoints(axis, rvec, tvec, camera_matrix, dist_coeffs)

    # Draw pose axes
    center = np.mean(image_points, axis=0).astype(int)
    frame = cv2.line(frame, tuple(center), tuple(imgpts[0].ravel().astype(int)), (255, 0, 0), 2)
    frame = cv2.line(frame, tuple(center), tuple(imgpts[1].ravel().astype(int)), (0, 255, 0), 2)
    frame = cv2.line(frame, tuple(center), tuple(imgpts[2].ravel().astype(int)), (0, 0, 255), 2)

    # Display pose text at object center
    cx = int(np.mean(image_points[:, 0]))
    cy = int(np.mean(image_points[:, 1]))
    pose_text = f"{label}: T=({t[0]:.2f},{t[1]:.2f},{t[2]:.2f}) R=({r[0]:.1f},{r[1]:.1f},{r[2]:.1f})"
    cv2.putText(frame, pose_text, (cx - 100, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    return frame


def detect_cube(hsv):
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            return box.astype(np.int32)
    return None


def detect_screwdriver(hsv):
    lower_color = np.array([45, 100, 50])
    upper_color = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_color, upper_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            return box.astype(np.int32)
    return None


# ✅ RealSense camera stream
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 30)
pipeline.start(config)

print("Press 'd' to print cube pose, 'j' for screwdriver pose, 'q' to quit")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cube_box = detect_cube(hsv)
        screwdriver_box = detect_screwdriver(hsv)

        key = cv2.waitKey(1) & 0xFF

        if cube_box is not None:
            object_points_cube = np.float32([
                [-cube_size / 2, -cube_size / 2, 0],
                [cube_size / 2, -cube_size / 2, 0],
                [cube_size / 2, cube_size / 2, 0],
                [-cube_size / 2, cube_size / 2, 0]
            ])
            image_points_cube = np.float32(cube_box)
            t, r, rvec, tvec = get_pose(object_points_cube, image_points_cube)
            if t is not None:
                frame = draw_pose(frame, image_points_cube, rvec, tvec, "Cube", t, r)
                if key == ord('d'):
                    print("Cube 6D Pose:")
                    print("Translation (m):", t)
                    print("Rotation (Euler degrees):", r)

        if screwdriver_box is not None:
            object_points_screw = np.float32([
                [-screwdriver_radius, 0, 0],
                [screwdriver_radius, 0, 0],
                [screwdriver_radius, 0, screwdriver_height],
                [-screwdriver_radius, 0, screwdriver_height]
            ])
            image_points_screw = np.float32(screwdriver_box)
            t, r, rvec, tvec = get_pose(object_points_screw, image_points_screw)
            if t is not None:
                frame = draw_pose(frame, image_points_screw, rvec, tvec, "Screwdriver", t, r)
                if key == ord('j'):
                    print("Screwdriver 6D Pose:")
                    print("Translation (m):", t)
                    print("Rotation (Euler degrees):", r)

        cv2.imshow("6D Pose Detection", frame)
        if key == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
