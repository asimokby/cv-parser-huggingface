import re
import os
import logging
import docx
import pdfplumber

class ResumeReader:

    def convert_docx_to_txt(self, docx_file,docx_parser):
        """
            A utility function to convert a Microsoft docx files to raw text.

            This code is largely borrowed from existing solutions, and does not match the style of the rest of this repo.
            :param docx_file: docx file with gets uploaded by the user
            :type docx_file: InMemoryUploadedFile
            :return: The text contents of the docx file
            :rtype: str
        """
      
        doc = docx.Document(docx_file)
        allText = []
        for docpara in doc.paragraphs:
            allText.append(docpara.text)
        text = ' '.join(allText)
        try:
            clean_text = re.sub(r'\n+', '\n', text)
            clean_text = clean_text.replace("\r", "\n").replace("\t", " ")  # Normalize text blob
            resume_lines = clean_text.splitlines()  # Split text blob into individual lines
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if
                            line.strip()]  # Remove empty strings and whitespaces
            return resume_lines, text
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "

    def convert_pdf_to_txt(self, pdf_file):
        """
        A utility function to convert a machine-readable PDF to raw text.

        This code is largely borrowed from existing solutions, and does not match the style of the rest of this repo.
        :param input_pdf_path: Path to the .pdf file which should be converted
        :type input_pdf_path: str
        :return: The text contents of the pdf
        :rtype: str
        """

        pdf = pdfplumber.open(pdf_file)
        raw_text= ""
       
        for page in pdf.pages:
            raw_text += page.extract_text() + "\n"

        pdf.close()                
      
        try:
            full_string = re.sub(r'\n+', '\n', raw_text)
            full_string = full_string.replace("\r", "\n")
            full_string = full_string.replace("\t", " ")

            # Remove awkward LaTeX bullet characters
            full_string = re.sub(r"\uf0b7", " ", full_string)
            full_string = re.sub(r"\(cid:\d{0,3}\)", " ", full_string)
            full_string = re.sub(r'• ', " ", full_string)

            # Split text blob into individual lines
            resume_lines = full_string.splitlines(True)

            # Remove empty strings and whitespaces
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]
           
            return resume_lines, raw_text 
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "

    def read_file(self, file,docx_parser = "tika"):
        """
        file : Give path of resume file
        docx_parser : Enter docx2txt or tika, by default is tika
        """
        # file = "/content/Asst Manager Trust Administration.docx"
        file = os.path.join(file)
        if file.endswith('docx') or file.endswith('doc'):
            # if file.endswith('doc') and docx_parser == "docx2txt":
                # docx_parser = "tika"
                # logging.error("doc format not supported by the docx2txt changing back to tika")
            resume_lines, raw_text = self.convert_docx_to_txt(file,docx_parser)
        elif file.endswith('pdf'):
            resume_lines, raw_text = self.convert_pdf_to_txt(file)
        elif file.endswith('txt'):
            with open(file, 'r', encoding='utf-8') as f:
                resume_lines = f.readlines()

        else:
            resume_lines = None
        
        # print(resume_lines)
      
        return resume_lines 