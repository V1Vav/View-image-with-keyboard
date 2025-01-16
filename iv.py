import pygame
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory
import re

# Node class for the linked list
class ImageNode:
    def __init__(self, path):
        self.path = path
        self.next = None
        self.prev = None
        self.image = None  # Store the image here for later use

# Linked list class
class ImageLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def add_image(self, path):
        """Add a new image node to the linked list."""
        new_node = ImageNode(path)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def set_current(self, node):
        """Set the current node."""
        self.current = node

    def next_image(self):
        """Move to the next image."""
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current
        return None

    def prev_image(self):
        """Move to the previous image."""
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current
        return None

def sort_images(image_list):
    def image_key(image_name):
        match = re.search(r'(\d+)', image_name)
        return int(match.group(1)) if match else float('inf')
    
    return sorted(image_list, key=image_key)

# Function to choose a folder
def choose_folder():
    """Open a popup to choose a folder and return its path."""
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_path = askdirectory(title="Select Folder Containing Images")
    if not folder_path:
        raise ValueError("No folder selected.")
    return folder_path

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 1920, 1080  # Set window size to 1920x1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Image Viewer")

# Variables for image handling
folder_path = choose_folder()  # Open folder selection popup
image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
               if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', ".webp"))]
if not image_files:
    raise ValueError(f"No images found in folder: {folder_path}")

# Sort image files
image_files = sort_images(image_files)

# Load image paths into a linked list
image_list = ImageLinkedList()
for img_path in image_files:
    image_list.add_image(img_path)

# Set the initial image as the head
image_list.set_current(image_list.head)

# Initialize viewing parameters
zoom_factor = 1.0
offset_x, offset_y = 0, 0

def load_image(path):
    """Load the image and scale it."""
    img = pygame.image.load(path)
    return img.convert_alpha()

def draw_image(image):
    """Draw the image with zoom and pan adjustments."""
    global zoom_factor, offset_x, offset_y
    scaled_width = int(image.get_width() * zoom_factor)
    scaled_height = int(image.get_height() * zoom_factor)
    scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))
    screen.blit(scaled_image, (offset_x, offset_y))

# Load the first image
current_node = image_list.current
if not current_node.image:
    current_node.image = load_image(current_node.path)
current_image = current_node.image

# Main loop
running = True
while running:
    screen.fill((30, 30, 30))  # Background color
    
    # Draw the black box (double the size of the image)
    image_width, image_height = current_image.get_width(), current_image.get_height()
    black_box_width = image_width * 2
    black_box_height = image_height * 2
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, black_box_width, black_box_height))
    
    # Draw the current image
    draw_image(current_image)
    pygame.display.flip()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Exit with ESC
            if event.key == pygame.K_ESCAPE:
                running = False

            # Navigation
            if event.key == pygame.K_z:  # Previous image
                prev_node = image_list.prev_image()
                if prev_node and not prev_node.image:
                    prev_node.image = load_image(prev_node.path)  # Load the previous image
                current_image = prev_node.image if prev_node else current_image
            if event.key == pygame.K_x:  # Next image
                next_node = image_list.next_image()
                if next_node and not next_node.image:
                    next_node.image = load_image(next_node.path)  # Load the next image
                current_image = next_node.image if next_node else current_image

    # Key handling
    keys = pygame.key.get_pressed()

    # Zooming
    if keys[pygame.K_q]:
        zoom_factor += 0.01
    if keys[pygame.K_e]:
        zoom_factor = max(0.1, zoom_factor - 0.01)

    # Calculate minimum zoom factor to fit the image within the window
    min_zoom = min(screen_width / image_width, screen_height / image_height)  # Ensure the image fits in the window
    zoom_factor = min(max(min_zoom, zoom_factor), 5)  # Set a limit for zoom factor

    # Calculate the scaled width and height of the current image
    scaled_width = int(image_width * zoom_factor)
    scaled_height = int(image_height * zoom_factor)

    # Panning logic: Only allow movement if the image hasn't reached the window edge
    if scaled_width > screen_width:
        if keys[pygame.K_a] and offset_x < 0:  # Move left
            offset_x += 10
        if keys[pygame.K_d] and offset_x > screen_width - scaled_width:  # Move right
            offset_x -= 10
    else:
        offset_x = (screen_width - scaled_width) // 2  # Center the image if smaller than screen width

    if scaled_height > screen_height:
        if keys[pygame.K_w] and offset_y < 0:  # Move up
            offset_y += 10
        if keys[pygame.K_s] and offset_y > screen_height - scaled_height:  # Move down
            offset_y -= 10
    else:
        offset_y = (screen_height - scaled_height) // 2  # Center the image if smaller than screen height

# Quit Pygame
pygame.quit()
