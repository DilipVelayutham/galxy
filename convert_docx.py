import os
import zipfile
import xml.etree.ElementTree as ET

def docx_to_text(docx_path):
    try:
        WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        TEXT = WORD_NAMESPACE + 't'
        PARA = WORD_NAMESPACE + 'p'
        TBL = WORD_NAMESPACE + 'tbl'
        TR = WORD_NAMESPACE + 'tr'
        TC = WORD_NAMESPACE + 'tc'
        
        with zipfile.ZipFile(docx_path) as docx:
            tree = ET.parse(docx.open('word/document.xml'))
            root = tree.getroot()
            
            output = []
            
            # Helper to extract text from a paragraph
            def get_para_text(p_node):
                return ''.join(t_node.text for t_node in p_node.iter(TEXT) if t_node.text)
            
            # We can traverse the elements under the body tag.
            # The body is usually root[0] or root.find(WORD_NAMESPACE + 'body')
            body = root.find(WORD_NAMESPACE + 'body')
            if body is None:
                # Fallback to root iter
                body = root
                
            for child in body:
                tag = child.tag
                if tag == PARA:
                    txt = get_para_text(child)
                    if txt:
                        output.append(txt + "\n")
                elif tag == TBL:
                    # It's a table. Format as a simple text table/grid
                    output.append("\n--- Table Start ---")
                    for row in child.iter(TR):
                        row_cells = []
                        for cell in row.iter(TC):
                            # Get all paragraph text inside this cell
                            cell_text = " ".join(get_para_text(p) for p in cell.iter(PARA)).strip()
                            row_cells.append(cell_text)
                        output.append(" | ".join(row_cells))
                    output.append("--- Table End ---\n")
                else:
                    # Let's extract any nested paragraphs/text
                    txt = get_para_text(child)
                    if txt:
                        output.append(txt + "\n")
            return "\n".join(output)
    except Exception as e:
        return f"Error reading {docx_path}: {e}"

def main():
    files = [
        "2_Ilakya_SL_Backend_AdminAPI.docx",
        "Galxy_Module3_Products.docx",
        "Galxy_Project_Plan (1).docx"
    ]
    for f in files:
        if os.path.exists(f):
            print(f"Converting {f}...")
            txt_content = docx_to_text(f)
            out_name = f.replace(".docx", ".md")
            with open(out_name, "w", encoding="utf-8") as out_f:
                out_f.write(txt_content)
            print(f"Saved to {out_name}")
        else:
            print(f"File {f} not found!")

if __name__ == "__main__":
    main()
