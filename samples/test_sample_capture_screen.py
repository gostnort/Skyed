import numpy as np
from PIL import Image, ImageChops
import mss
import time

def capture_screen():
    with mss.mss() as sct:
        # Capture the entire screen
        screenshot = sct.grab(sct.monitors[1])
        # Convert to Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

def find_differences(img1, img2):
    # Ensure the images are the same size
    if img1.size != img2.size:
        raise ValueError("Images must be the same size for comparison")
    
    # Calculate the difference between the two images
    diff = ImageChops.difference(img1, img2)
    
    # Convert to grayscale
    diff = diff.convert('L')
    
    # Convert to numpy array
    diff_array = np.array(diff)
    
    # Find coordinates of non-zero differences
    y_coords, x_coords = np.nonzero(diff_array)
    
    if len(y_coords) == 0 or len(x_coords) == 0:
        return None
    
    # Get bounding box coordinates
    top, left = y_coords.min(), x_coords.min()
    bottom, right = y_coords.max(), x_coords.max()
    
    return (left, top, right, bottom)

def calculate_pixel_difference(diff):
    # Calculate the number of different pixels
    num_diff_pixels = np.count_nonzero(np.array(diff))
    
    # Calculate the total number of pixels
    total_pixels = diff.size[0] * diff.size[1]
    
    # Calculate the percentage of different pixels
    diff_percentage = (num_diff_pixels / total_pixels) * 100
    
    return diff_percentage

def main():
    # Capture the initial screen content
    print("Capturing the initial screen content...")
    img1 = capture_screen()
    
    # Wait or perform some operations here
    input("Press Enter after changing the screen content to capture the new screen content...\n")
    
    # Capture the new screen content
    print("Capturing the new screen content...")
    img2 = capture_screen()
    
    # Find the differences
    print("Finding differences...")
    bbox = find_differences(img1, img2)
    
    if bbox:
        left, top, right, bottom = bbox
        print(f"Changed area coordinates: Left={left}, Top={top}, Right={right}, Bottom={bottom}")
        
        # Crop the different area from the images
        diff_img1 = img1.crop(bbox)
        diff_img2 = img2.crop(bbox)

        # Save the cropped images
        diff_img1.save("initial_cropped.png")
        diff_img2.save("new_cropped.png")
        print("Cropped images saved as 'initial_cropped.png' and 'new_cropped.png'")
        
        # Calculate the pixel difference in the changed area
        diff = ImageChops.difference(diff_img1, diff_img2)
        diff_percentage = calculate_pixel_difference(diff)
        
        print(f"Percentage of pixel difference in the changed area: {diff_percentage:.2f}%")
    else:
        print("No differences found.")

if __name__ == "__main__":
    main()
