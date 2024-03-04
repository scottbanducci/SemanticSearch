import os
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO
import pathlib
import shutil

cache_folder_path = r"data\cached_pdfs"

def convert_pdf_folder_to_text(processed_files_folder, input_folder, selected_pdfs):
    
    # list to return the names of all files converted
    successfully_converted_pdfs = []
    skipped_pdfs = []


    # for each pdf file in input folder...
    for pdf_file in selected_pdfs:
        pdf_path = pathlib.Path(input_folder, pdf_file)

        # check if it has already been processed into text
        if pdf_file[:-4] in os.listdir(processed_files_folder):
            skipped_pdfs.append(pdf_file + " (already exists)")
            continue


        # check if file is pdf and create a new folder for it to store text files
        elif pdf_file.endswith(".pdf"):
            pdf_path = pathlib.Path(input_folder, pdf_file)
            pdf_text_folder = pathlib.Path(processed_files_folder, pdf_file[:-4])
            pathlib.Path(pdf_text_folder).mkdir(parents=True, exist_ok=True)

            # open and convert each page to text
            with open(pdf_path, 'rb') as fh:
                for page_num in range(1,10000):                     # arbitrary high number
                    output_string = StringIO()
                    laparams = LAParams()
                    try:
                        extract_text_to_fp(fh, output_string, laparams=laparams, page_numbers=[page_num-1])
                        text = output_string.getvalue()
                        if not text:                                # Break the loop if there's no text (end of document)
                            break 

                        # save text to file
                        with open(f"{pdf_text_folder}/page_{page_num}.txt", "w", encoding="utf-8") as text_file:
                            text_file.write(text)
                    
                    # catch errors
                    except Exception as e:
                        print(f"Error processing page {page_num} of {pdf_file}: {e}")
                        break

            # move the processed pdf to the cached_pdfs folder
            processed_pdf_path = pathlib.Path(cache_folder_path, pdf_file)
            if not processed_pdf_path.exists():                     # check if the pdf file already exists in the cached_pdfs
                shutil.move(pdf_path, processed_pdf_path)
            successfully_converted_pdfs.append(pdf_file)

    if not successfully_converted_pdfs:
        res = ["No pdfs converted"]
        return res, skipped_pdfs

    return successfully_converted_pdfs, skipped_pdfs