import os
import re
import fitz  # PyMuPDF

import logging
import json

# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Extractor:
    @staticmethod
    def _create_directories(save_dir):
        """Create necessary directories for saving extracted content."""
        os.makedirs(os.path.join(save_dir, "texts"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "tables"), exist_ok=True)

    @staticmethod
    def _extract_text_from_page(page, text_dir, page_number):
        """Extract text from a single page and save it to a file."""
        text = page.get_text()
        report_indicator = re.compile(r"[Rr]esearch\s+[Rr]eport\s+[Nn]o\.")
        if report_indicator.match(text.split("\n")[0]):
            text_list = text.split("\n")[1:-3]
        else:
            text_list = text.split("\n")
        text = "\n".join(text_list)
        with open(os.path.join(text_dir, f"output_{page_number}.txt"), "w") as out:
            out.write(text)
        return text

    @staticmethod
    def _extract_images_from_page(page, image_dir, page_number):
        """Extract images from a single page and save them as PNG files."""
        image_list = page.get_images()
        if image_list:
            print(f"Found {len(image_list)} images on page {page_number}")
        else:
            print("No images found on page", page_number)
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)
            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            try:
                pix.save(
                    os.path.join(
                        image_dir, f"page_{page_number}-image_{image_index}.png"
                    )
                )
            except Exception:
                continue

    @staticmethod
    def _save_whole_content(text_dir, whole_content):
        """Save the whole content of the PDF to a file."""
        with open(os.path.join(text_dir, "content.txt"), "w") as file:
            file.write(whole_content)

    @staticmethod
    def _clean_content(whole_content):
        """Clean the content by removing text from tables and figures, and extract descriptions."""
        lines = whole_content.split("\n")
        clean_lines, figure_descriptions, table_descriptions = [], [], []
        abbreviations_table = {}
        figure_pattern = re.compile(r"^Figure \d+:")
        table_pattern = re.compile(r"^Table \d+:")
        # abbr_pattern = re.compile(r"Short Name")
        num_lines = len(lines)
        curr_line = 0
        while curr_line < num_lines:
            line = lines[curr_line]

            if line.strip().startswith("Short Name"):
                Extractor._process_abbreviation(
                    lines, curr_line, num_lines, abbreviations_table
                )
                curr_line += 1
            elif figure_pattern.match(line):
                curr_line = Extractor._process_figure_description(
                    lines, curr_line, num_lines, clean_lines, figure_descriptions
                )
            elif table_pattern.match(line):
                curr_line = Extractor._process_table_description(
                    lines,
                    curr_line,
                    num_lines,
                    clean_lines,
                    table_descriptions,
                    abbreviations_table,
                )

            else:
                clean_lines.append(line)
                _line = line
                if curr_line + 1 < num_lines:
                    _line = _line + " " + lines[curr_line + 1]
                extracted_abbr = extract_abbreviation(_line)
                if extracted_abbr:
                    abbreviations_table.update(extracted_abbr)
                curr_line += 1
        clean_text = "\n".join(clean_lines)
        return clean_text, figure_descriptions, table_descriptions, abbreviations_table

    @staticmethod
    def _process_abbreviation(lines, curr_line, num_lines, abbreviations_table):
        while True:
            inloop_line = lines[curr_line]
            if inloop_line.endswith(".") or len(inloop_line.split()) > 8:
                break
            else:
                if inloop_line.isupper():
                    # if is_alpha_hyphen(lines[curr_line+1]):
                    abbreviations_table.update({inloop_line: lines[curr_line + 1]})

                curr_line += 1

    @staticmethod
    def _process_figure_description(
        lines, curr_line, num_lines, clean_lines, figure_descriptions
    ):
        """Process and extract figure descriptions."""
        # logging.info(lines[curr_line+1])
        while True:
            inloop_line = clean_lines.pop()
            if inloop_line.endswith(".") or len(inloop_line.split()) > 7:
                # logging.info(inloop_line)
                clean_lines.append(inloop_line)
                break
        description_range = 0
        while description_range < 10 and curr_line + description_range < num_lines:
            inloop_line = lines[curr_line + description_range]
            description_range += 1
            clean_lines.append(inloop_line)
            if inloop_line.endswith("."):
                description = " ".join(
                    line.rstrip("\n")
                    for line in lines[curr_line : curr_line + description_range]
                )
                figure_descriptions.append(description)
                break

        return curr_line + description_range

    @staticmethod
    def _process_table_description(
        lines,
        curr_line,
        num_lines,
        clean_lines,
        table_descriptions,
        abbreviations_table,
    ):
        """Process and extract table descriptions."""
        description_range = 0
        while description_range < 10 and curr_line + description_range < num_lines:
            inloop_line = lines[curr_line + description_range]

            clean_lines.append(inloop_line)
            if inloop_line.endswith("."):
                description = " ".join(
                    line.rstrip("\n")
                    for line in lines[curr_line : curr_line + description_range + 1]
                )
                table_descriptions.append(description)
                break
            description_range += 1
        curr_line = curr_line + description_range + 1
        while curr_line < num_lines:
            inloop_line = lines[curr_line]
            if inloop_line.strip().startswith("Short Name"):
                Extractor._process_abbreviation(
                    lines, curr_line, num_lines, abbreviations_table
                )

            if len(inloop_line.split()) > 9 or inloop_line.endswith("."):
                break
            curr_line += 1
        return curr_line

    @staticmethod
    def _save_clean_content(text_dir, clean_text):
        """Save cleaned content to a file."""
        with open(os.path.join(text_dir, "clean_content.txt"), "w") as file:
            file.write(clean_text)

    @staticmethod
    def _save_abbreviations_table(table_dir, abbreviations_table):
        with open(os.path.join(table_dir, "abbreviations.json"), "w") as file:
            json.dump(abbreviations_table, file)

    @staticmethod
    def _save_descriptions(
        image_dir, table_dir, figure_descriptions, table_descriptions
    ):
        """Save figure and table descriptions to separate files."""
        with open(os.path.join(image_dir, "figure_descriptions.txt"), "w") as file:
            file.write("\n".join(figure_descriptions))
        with open(os.path.join(table_dir, "table_descriptions.txt"), "w") as file:
            file.write("\n".join(table_descriptions))

    @staticmethod
    def extract_file(file_name, save_dir):
        """
        Extract and organize content from a PDF file.

        Args:
            file_name (str): Path to the PDF file.
            save_dir (str): Directory for saving the results.
        """
        doc = fitz.open(file_name)
        Extractor._create_directories(save_dir)
        text_dir = os.path.join(save_dir, "texts")
        image_dir = os.path.join(save_dir, "images")
        table_dir = os.path.join(save_dir, "tables")

        whole_content = []
        for page_number, page in enumerate(doc.pages(), start=1):
            text = Extractor._extract_text_from_page(page, text_dir, page_number)
            whole_content.append(text)
            Extractor._extract_images_from_page(page, image_dir, page_number)

        whole_content = "\n".join(whole_content)
        Extractor._save_whole_content(text_dir, whole_content)

        (
            clean_text,
            figure_descriptions,
            table_descriptions,
            abbreviations_table,
        ) = Extractor._clean_content(whole_content)
        Extractor._save_clean_content(text_dir, clean_text)
        Extractor._save_abbreviations_table(table_dir, abbreviations_table)
        Extractor._save_descriptions(
            image_dir, table_dir, figure_descriptions, table_descriptions
        )


def extract_abbreviation(line):
    # Regular expression to find patterns like 'Micro Humidity Sounder (MHS)' or 'MHS (Micro Humidity Sounder)'
    pattern = re.compile(r"([A-Za-z- ]+)?\s?\(([A-Z]+)\)|([A-Z]+)\s?\(([A-Za-z- ]+)\)")

    match = pattern.search(line)
    if not match:
        return None

    full_form = abbreviation = None

    if match.group(1) and match.group(2):
        full_form = match.group(1).strip()
        abbreviation = match.group(2).strip()
    elif match.group(3) and match.group(4):
        abbreviation = match.group(3).strip()
        full_form = match.group(4).strip()

    if not full_form or not abbreviation:
        return None

    # Validate if abbreviation matches the initials of the full form
    initials = "".join(word[0].upper() for word in full_form.split())
    if initials == abbreviation:
        return {abbreviation: full_form}

    return None


# def is_alpha_hyphen(string):
#     allowed_characters = ["-", " ", "*"]
#     return all(c.isalpha() or c == "-" or c == " " for c in string)
