import fitz
import os
import shutil
import camelot

DOCS_DIRECTORY = "/home/user/large-disk/crawled_resources/"
output_subdirectory = {
#    "memoranda": "technical_memoranda",
    "ERA": "ERA_Reports",
#    "esa-eumetsat": "esa_eumetsat_contract_reports",
    "eumetsat-ecmwf": "eumetsat_ecmwf_fellowship_programme_research_reports",
    "report": "reports",
    # 'newsletter':"newsletter"
}

def extract_file(file_name, save_dir):

    doc = fitz.open(file_name)
    tables = camelot.read_pdf(file_name)
    
    text_dir = os.path.join(save_dir, "texts")
    os.makedirs(text_dir, exist_ok=True)
    
    image_dir = os.path.join(save_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    table_dir = os.path.join(save_dir, "tables")
    os.makedirs(table_dir, exist_ok=True)

    for pageNumber, page in enumerate(doc.pages(), start=1):
        # extract texts from here
        text = page.get_text().encode("utf8")

        with open(os.path.join(text_dir, f"output_{pageNumber}.txt"), "wb") as out:
            out.write(text)  # write text of page
            out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)



        # extract images from here
        page = doc[pageNumber-1] # get the page
        image_list = page.get_images()

        # print the number of images found on the page
        if image_list:
            print(f"Found {len(image_list)} images on page {pageNumber}")
        else:
            print("No images found on page", pageNumber)

        for image_index, img in enumerate(image_list, start=1): # enumerate the image list
            xref = img[0] # get the XREF of the image
            pix = fitz.Pixmap(doc, xref) # create a Pixmap

            if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)
            try:
                pix.save(os.path.join(image_dir, "page_%s-image_%s.png" % (pageNumber, image_index))) # save the image as png
            except:
                continue
            pix = None


    for tableNumber, table in enumerate(tables):
        table_file = os.path.join(table_dir, f"{tableNumber}_table.csv")
        table.to_csv(table_file)


### The following block move all pdf into a folder with the same name

for key, value in output_subdirectory.items():
    directory_folder = DOCS_DIRECTORY + value
    files_and_dirs = os.listdir(DOCS_DIRECTORY + value)
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(directory_folder, f))]
    for file in files:
        file = os.path.join(directory_folder, file)
        directory_file = os.path.join(directory_folder, file[:-4])
        os.makedirs(directory_file, exist_ok=True)
        shutil.move(file, directory_file)


### The following block extract the pdf inside the folder into three dir: texts, images, tables

for key, value in output_subdirectory.items():
    directory_folder = DOCS_DIRECTORY + value
    files_and_dirs = os.listdir(DOCS_DIRECTORY + value)
    dirs = [f for f in files_and_dirs if os.path.isdir(os.path.join(directory_folder, f))]
    for directory in dirs:
        curr_dir = os.path.join(directory_folder, directory)
        print(curr_dir)
        entries = os.listdir(curr_dir)
        pdf_files = [f for f in entries if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(curr_dir, f))]
        if len(pdf_files) > 1:
            raise Exception("The number of pdf in each folder should be 1!")
        file = pdf_files[0]
        full_file = os.path.join(curr_dir, file)
        extract_file(full_file, curr_dir)