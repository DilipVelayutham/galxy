import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def get_docx_text(path):
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    TEXT = WORD_NAMESPACE + 't'
    PARA = WORD_NAMESPACE + 'p'
    
    try:
        with zipfile.ZipFile(path) as docx:
            tree = ET.fromstring(docx.read('word/document.xml'))
            paragraphs = []
            for paragraph in tree.iter(PARA):
                texts = [node.text for node in paragraph.iter(TEXT) if node.text]
                paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error reading {path}: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python read_docx.py <path_to_docx> <path_to_output_txt>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_path = sys.argv[2]
    text = get_docx_text(file_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Successfully wrote to {output_path}")

