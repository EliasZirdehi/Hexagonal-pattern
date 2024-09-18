import io
import svgwrite
import math
from PIL import Image, ImageOps, ImageDraw, ImageFilter
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation, grey_erosion
import streamlit as st
from PIL import Image as PILImage

def hexagon_vertices(cx, cy, side_length):
    """Calculate the vertices of a hexagon centered at (cx, cy) with a given side length."""
    angle_deg = 60
    angle_rad = math.pi / 180 * angle_deg
    return [
        (cx + side_length * math.cos(angle_rad * i), cy + side_length * math.sin(angle_rad * i))
        for i in range(6)
    ]

def create_hexagonal_lattice(
    svg_buffer,
    hex_side_length: int = 30,
    lattice_constant: int = 50,
    width: int = 800,
    height: int = 800,
    fill: str = "darkcyan",
    stroke: str = "none",
    sw: int = 0,
    opacity: float = 1.0,
    gradient_field=None):
    """
    Create a hexagonal lattice of filled hexagons with a specified lattice constant.
    """
    horizontal_distance = lattice_constant * math.sqrt(3)
    vertical_distance = lattice_constant / 2

    dwg = svgwrite.Drawing(debug=True, size=(width, height))

    n_x = math.ceil(width / horizontal_distance) - 1
    n_y = math.ceil(height / vertical_distance) - 1

    for row in range(n_y):
        for col in range(n_x):
            cx = col * horizontal_distance
            cy = row * vertical_distance

            if row % 2 == 1:
                cx += horizontal_distance / 2

            if gradient_field is not None:
                img_x = min(int(col / n_x * gradient_field.shape[1]), gradient_field.shape[1] - 1)
                img_y = min(int(row / n_y * gradient_field.shape[0]), gradient_field.shape[0] - 1)
                intensity = gradient_field[img_y, img_x]
                if math.isclose(intensity, 0.0, rel_tol=1e-3, abs_tol=1e-1):
                    continue
                scaled_side_length = max(1, intensity * hex_side_length)
            else:
                scaled_side_length = hex_side_length

            vertices = hexagon_vertices(cx, cy, scaled_side_length)
            dwg.add(dwg.polygon(points=vertices, stroke=stroke, stroke_width=sw, fill=fill, opacity=opacity))

    dwg.write(svg_buffer)

def generate_gradient_field_from_image(image_path, width=500, height=500, normalize=False, smoothing_strength=0, dilation_pixels=0):
    """Load a grayscale image, resize it, and generate a gradient field based on pixel intensity."""
    image = Image.open(image_path).convert("L")
    image = ImageOps.cover(image, (width, height), method=Image.Resampling.LANCZOS)
    image_data = np.array(image) / 255.0

    if dilation_pixels != 0:
        if dilation_pixels > 0:
            image_data = grey_dilation(image_data, size=(dilation_pixels,dilation_pixels), mode='reflect').astype(float)
        else:
            image_data = grey_erosion(image_data, size=(-dilation_pixels,-dilation_pixels), mode='reflect').astype(float)

    if smoothing_strength > 0:
        image_data = gaussian_filter(image_data, sigma=smoothing_strength)
    
    if normalize:
        min_val = np.min(image_data)
        max_val = np.max(image_data)
        if max_val > min_val:
            image_data = (image_data - min_val) / (max_val - min_val)

    image_data = 1 - image_data
    return image_data

def draw_lattice_on_image(hex_side_length, lattice_constant, width, height, gradient_field, hex_color, background_color, transparent_background):
    """Draw the hexagonal lattice onto a higher resolution image with optional background transparency."""
    scale_factor = 4
    hex_side_length_upscaled = hex_side_length * scale_factor
    high_res_width, high_res_height = width * scale_factor, height * scale_factor

    if transparent_background:
        img = PILImage.new("RGBA", (high_res_width, high_res_height), (0, 0, 0, 0))  # Transparent background
    else:
        img = PILImage.new("RGB", (high_res_width, high_res_height), background_color)  # Solid background

    draw = ImageDraw.Draw(img)

    horizontal_distance = lattice_constant * math.sqrt(3) * scale_factor
    vertical_distance = lattice_constant / 2 * scale_factor

    n_x = math.ceil(high_res_width / horizontal_distance) - 1
    n_y = math.ceil(high_res_height / vertical_distance) - 1

    for row in range(n_y):
        for col in range(n_x):
            cx = col * horizontal_distance
            cy = row * vertical_distance

            if row % 2 == 1:
                cx += horizontal_distance / 2

            if gradient_field is not None:
                img_x = min(int(col / n_x * gradient_field.shape[1]), gradient_field.shape[1] - 1)
                img_y = min(int(row / n_y * gradient_field.shape[0]), gradient_field.shape[0] - 1)
                intensity = gradient_field[img_y, img_x]
                if math.isclose(intensity, 0.0, rel_tol=1e-3, abs_tol=1e-1):
                    continue
                scaled_side_length = max(1, intensity * hex_side_length_upscaled)
            else:
                scaled_side_length = hex_side_length_upscaled

            vertices = hexagon_vertices(cx, cy, scaled_side_length)
            draw.polygon(vertices, fill=hex_color)

    # Apply anti-aliasing by resizing the image down
    img = img.resize((width, height), resample=Image.LANCZOS)
    return img

def main():
    st.set_page_config(layout="wide")

    with st.sidebar:
        uploaded_file = st.file_uploader("Choose a grayscale image ...", type=["png", "jpg", "jpeg"])
        lattice_constant = st.slider("Lattice Constant", min_value=4, max_value=50, value=12)
        max_HexSL = round(lattice_constant / math.sqrt(3)) + 2
        hex_side_length = st.slider("Hexagon Side Length (Pixels)", min_value=min(max_HexSL-3, 4), max_value=max_HexSL, value=max_HexSL-3)
        width = st.slider("Image Width", min_value=100, max_value=1000, value=1000)
        height = st.slider("Image Height", min_value=100, max_value=1000, value=700)
        normalize = st.checkbox("Normalize Gradient Field", value=True)
        smoothing_strength = st.slider("Smooth Edges", min_value=0, max_value=20, value=0)
        dilation_pixels = st.slider("Adjust Boundary (Dilation/Erosion)", min_value=-50, max_value=50, value=0)

        # Color picker for hexagon fill and background
        hex_color = st.color_picker("Select Hexagon Fill Color", "#008B8B")  # Default to darkcyan color
        background_color = st.color_picker("Select Background Color", "#FFFFFF")  # Default to white
        transparent_background = st.checkbox("Transparent Background", value=False)

    if uploaded_file is not None:
        gradient_field = generate_gradient_field_from_image(uploaded_file, width=width, height=height, normalize=normalize, smoothing_strength=smoothing_strength, dilation_pixels=dilation_pixels)

        # SVG Rendering in Main Tab
        svg_buffer = io.StringIO()
        create_hexagonal_lattice(
                svg_buffer,
                hex_side_length=hex_side_length,
                lattice_constant=lattice_constant,
                width=width,
                height=height,
                fill=hex_color,
                stroke="tomato",
                sw=0,
                opacity=1.0,
                gradient_field=gradient_field
        )
        svg_content = svg_buffer.getvalue()

        st.write("### Generated Hexagonal Lattice")
        st.components.v1.html(svg_content, height=height, width=width)

        # Higher Resolution PNG/JPG Saving in a Separate Tab
        with st.expander("Save Image (High Resolution)", expanded=False):
            high_res_image = draw_lattice_on_image(hex_side_length, lattice_constant, width, height, gradient_field, hex_color, background_color, transparent_background)

            # Saving PNG file in memory
            png_buffer = io.BytesIO()
            if transparent_background:
                high_res_image.save(png_buffer, format="PNG")  # Transparent PNG
            else:
                high_res_image.save(png_buffer, format="PNG")  # Solid background PNG
            png_buffer.seek(0)  # Rewind buffer to beginning

            # Saving JPG file in memory (JPG does not support transparency)
            jpg_buffer = io.BytesIO()
            high_res_image.convert("RGB").save(jpg_buffer, format="JPEG", quality=99)  # Solid background JPG
            jpg_buffer.seek(0)  # Rewind buffer to beginning

            # Display download buttons
            st.download_button("Download PNG", data=png_buffer, file_name="lattice.png", mime="image/png")
            st.download_button("Download JPG", data=jpg_buffer, file_name="lattice.jpg", mime="image/jpeg")

        # SVG Save Button
        st.download_button("Download SVG", data=svg_content, file_name="lattice.svg", mime="image/svg+xml")

if __name__ == "__main__":
    main()
