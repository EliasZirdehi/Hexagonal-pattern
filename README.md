# Hexagonal Lattice Generator

This project is a **fun exploration** and a **test of the deployment process** for Streamlit apps. It generates a customizable hexagonal lattice pattern based on an input grayscale image, allowing users to experiment with various lattice parameters such as hexagon size, color, and image dimensions. The app can output images in both **SVG** and **PNG/JPG** formats, with the option for a **transparent background**.

## Features

- Upload any grayscale image (PNG/JPG).
- Adjustable hexagon lattice parameters:
  - Lattice constant (distance between hexagons)
  - Hexagon side length
  - Image dimensions
  - Smoothing and boundary adjustments for the gradient field
- Customizable colors for the hexagons and background, with an option for a transparent background.
- Download generated patterns in high-resolution **PNG/JPG** or **SVG** format.
  
## Requirements

To run this app locally, you’ll need:

- Python 3.x
- Streamlit
- Pillow
- svgwrite
- numpy
- scipy

Install the required packages using:

```bash
pip install streamlit Pillow svgwrite numpy scipy

## How to Run

1- Clone this repository:

git clone https://github.com/yourusername/hexagonal-lattice-generator.git
cd hexagonal-lattice-generator

2- Run the app with Streamlit:

streamlit run app.py

3- The app will open in your browser, and you can start generating hexagonal lattice patterns!

## License

This project is open-source under the MIT License.

Enjoy playing around with the Hexagonal Lattice Generator!


### Updates:
- Added the live demo link: `https://share.streamlit.io/app/hexagonal-pattern/`.

Feel free to experiment with the code and adjust parameters to create your own unique patterns!
