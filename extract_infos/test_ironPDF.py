from ironpdf import *

input_file = "/home/user/large-disk/crawled_resources/reports/7931-all-sky-assimilation-ssmis-humidity-sounding-channels-over-land-within-ecmwf-system/7931-all-sky-assimilation-ssmis-humidity-sounding-channels-over-land-within-ecmwf-system.pdf"

output_dir = "me/user/large-disk/crawled_resources/reports/7931-all-sky-assimilation-ssmis-humidity-sounding-channels-over-land-within-ecmwf-system/images/"

# Open PDF file
pdf = PdfDocument.FromFile("") 
# Get all images found in PDF Document
all_images = pdf.ExtractAllImages()
# Save each image to the local disk image
for i, image in enumerate(all_images):
    output_dir_file = os.path.join(output_dir, f"output_image_{i}.png")
    image.SaveAs(output_dir_file)