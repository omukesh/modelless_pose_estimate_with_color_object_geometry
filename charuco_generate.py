import cv2
import numpy as np

# Define the ChArUco board parameters
squaresX = 4  # Number of chessboard squares along X direction
squaresY = 5  # Number of chessboard squares along Y direction
squareLength = 0.035  # Length of the chessboard squares in meters
markerLength = 0.02  # Length of the ArUco markers in meters

# Create a ChArUco board
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
board = cv2.aruco.CharucoBoard((squaresX, squaresY), squareLength, markerLength, dictionary)

# Generate the ChArUco board image
img = board.generateImage((300, 400), marginSize=20)

# Save the image
cv2.imwrite("charuco_board.png", img)
