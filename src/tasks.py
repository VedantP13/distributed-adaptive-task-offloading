import hashlib
import time
import base64
import io
from PIL import Image, ImageFilter

# --- CONFIGURATION FOR PASSWORD CRACKING ---
# We use Base-36 (a-z, 0-9)
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
BASE = len(CHARSET)

def index_to_password(index, length):
    """
    Mathematically converts a numeric index to a password string (Base-36).
    Example: 0 -> 'aaaa', 1 -> 'aaab' ...
    """
    password = []
    for _ in range(length):
        password.append(CHARSET[index % BASE])
        index //= BASE
    return "".join(reversed(password))


# --- EXISTING MATRIX TASK ---
def execute_matrix_multiplication(n):
    print(f"Starting Matrix Multiplication (Size: {n}x{n})...")
    start_time = time.time()
    
    matrix_a = [[i for i in range(n)] for _ in range(n)]
    matrix_b = [[j for j in range(n)] for _ in range(n)]
    result = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    end_time = time.time()
    duration = end_time - start_time
    
    return {
        "status": "success",
        "matrix_size": n,
        "duration_seconds": duration,
        "node_id": "Worker_Node" 
    }


# --- EXISTING IMAGE TASK (Using PIL) ---
def apply_image_filter(image_data_base64, filter_type="BLUR"):
    """
    Receives a Base64 encoded image string, decodes it, applies a filter,
    and returns the processed image as a Base64 string.
    """
    print(f"Processing Image Task (Filter: {filter_type})...")
    start_time = time.time()

    try:
        # 1. Decode Base64 string back to binary
        image_data = base64.b64decode(image_data_base64)
        
        # 2. Open image using Pillow
        image = Image.open(io.BytesIO(image_data))
        
        # 3. Apply the requested filter
        if filter_type == "BLUR":
            # Radius 5 makes it very blurry (computationally intensive)
            processed_image = image.filter(ImageFilter.GaussianBlur(radius=5))
        elif filter_type == "CONTOUR":
            processed_image = image.filter(ImageFilter.CONTOUR)
        elif filter_type == "GRAYSCALE":
            processed_image = image.convert("L")
        else:
            processed_image = image # No filter
            
        # 4. Save processed image to a memory buffer (not disk)
        buffer = io.BytesIO()
        # Save as original format (e.g., JPEG or PNG) - default to JPEG if unknown
        img_format = image.format if image.format else 'JPEG'
        processed_image.save(buffer, format=img_format)
        buffer.seek(0)
        
        # 5. Encode back to Base64 to send over network
        processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"Image processed in {duration:.4f} seconds.")

        return {
            "status": "success",
            "image_data": processed_base64,
            "duration_seconds": duration,
            "node_id": "Worker_Node"
        }

    except Exception as e:
        print(f"Error processing image: {e}")
        return {"status": "error", "message": str(e)}


# --- UPDATED ALPHANUMERIC PASSWORD CRACKER ---
def crack_password_range(target_hash, start_index, end_index, length):
    """
    Brute-forces alphanumeric passwords in a specific numeric range.
    Args:
        target_hash: The MD5 hash we are trying to break.
        start_index: The starting number of the range.
        end_index: The ending number of the range.
        length: The length of the password (e.g., 4).
    """
    print(f"🔨 Cracking Range {start_index} - {end_index} (Len: {length})...")
    start_time = time.time()
    
    # Iterate through the assigned numeric range
    for i in range(start_index, end_index):
        # Convert number -> password string (e.g., 105 -> 'abc')
        current_pwd = index_to_password(i, length)
        
        # Hash it
        current_hash = hashlib.md5(current_pwd.encode()).hexdigest()
        
        if current_hash == target_hash:
            duration = time.time() - start_time
            print(f"🎉 FOUND IT! Password is: {current_pwd}")
            return {
                "status": "success",
                "password": current_pwd,
                "duration": duration,
                "node_id": "Worker_Node"
            }
            
    # If we finish the loop without finding it
    return {"status": "failure"}