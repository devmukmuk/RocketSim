import os
import csv
from PIL import Image, ImageDraw, ImageFont
import qrcode

def generate_qr(sheet_id, box_label=None, room_id=None, box_number=None, back_color_RGB=(255,255,255), create_color=False):
    """
    Generate a QR code that links directly to a specific box in a Google Sheet.
    
    :param sheet_id: The unique Google Sheet ID (found in the sheet URL).
    :param box_label: The label for the box to be displayed next to the QR code.
    :param back_color_RGB: The background color for the QR code image.
    :param label_color_RGB: The background color for the label.
    :param create_color: If True, create a color image with the label_color_RGB.
    :return: An image with the QR code and box label.
    """
    # Construct the link to highlight the specific box row in the Google Sheet
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"
    
    # print sheet_url
    print(f"URL: {sheet_url}")
    
    # max label length for the box label
    max_label_length = 3
    
    # if label_color_RGB is None, set it to white
    if create_color and back_color_RGB is None:
        back_color_RGB = get_rgb('white')
    elif not create_color:
        back_color_RGB = get_rgb('white')
    else:
        back_color_RGB = back_color_RGB 
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(sheet_url)
    qr.make(fit=True)
    
    # Create a QR code image with background color based on the label_color_RGB
    qr_img = qr.make_image(fill_color=(0,0,0), back_color=back_color_RGB)
    
    # resize the image to make it more readable
    qr_img = qr_img.resize((600, 600))
    
    # Create a new image with extra width to accommodate the text
    total_width = 1200  # Total width of the new image
    total_height = 600  # Height remains the same as the QR code image
    img = Image.new('RGB', (total_width, total_height), color=back_color_RGB)
    
    # Paste the QR code image on the left side
    img.paste(qr_img, (0, 0))
    draw = ImageDraw.Draw(img)
    
    # Add room_id text on right side top half
    if room_id:
        font_path = "arialbd.ttf"  # Replace with the path to your bold font file if needed
        font_size = 450  # Adjust the font size as needed
        font = ImageFont.truetype(font_path, font_size)
        text = f"{room_id}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((600,-50), text, fill='black', font=font)
        
    # Add box_number text on right side bottom half
    if box_number:
        font_path = "arialbd.ttf"  # Replace with the path to your bold font file if needed
        font_size = 250  # Adjust the font size as needed
        font = ImageFont.truetype(font_path, font_size)
        text = f"{box_number}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((700, 350), text, fill='black', font=font)
        
    # Return the image     
    return img

# Create a list of unique box colors with RGB values
unique_colors = [
    ((255, 0, 0), 'red'),        # Red
    ((0, 255, 0), 'green'),      # Green
    ((0, 0, 255), 'blue'),       # Blue
    ((255, 255, 0), 'yellow'),   # Yellow
    ((255, 165, 0), 'orange'),   # Orange
    ((128, 0, 128), 'purple'),   # Purple
    ((0, 255, 255), 'cyan'),     # Cyan
    ((255, 192, 203), 'pink'),   # Pink
    ((165, 42, 42), 'brown'),    # Brown
    ((0, 0, 0), 'black'),        # Black
    ((255, 255, 255), 'white'),   # White
    ((128, 128, 128), 'gray'),    # Gray
]

# define function to get RGB tuple from color name
def get_rgb(color_name):
    for rgb, name in unique_colors:
        if name.lower() == color_name.lower():
            return rgb
    return None

# define function to get color name from RGB tuple  
def get_color_name(rgb):
    for rgb_val, name in unique_colors:
        if rgb == rgb_val:
            return name
    return None

# Check and create the reports/qr_codes folder if it doesn't exist
if not os.path.exists("reports/qr_codes"):
    os.makedirs("reports/qr_codes")

# Read the data from the CSV file
csv_file = 'data/google_id.csv'
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        sheet_id, google_name = row
        try:
            room, room_id, box_number = google_name.split('-')
        except ValueError:
            print(f"Skipping invalid entry: {google_name}")
            continue

        # Generate the QR code
        img = generate_qr(sheet_id, google_name, room_id, box_number, get_rgb('gray'))

        # Save the image with the box label as the filename in the reports/qr_codes folder
        img.save(f"reports/qr_codes/{room_id}-{box_number}.png")

print("QR codes have been generated and saved to the reports/qr_codes folder.")
