import fitz
import os

def extract_pages(pdf_path, output_dir, page_ranges):
    doc = fitz.open(pdf_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for page_num in page_ranges:
        # page_num is 1-indexed for user convenience, fitz uses 0-indexed
        page = doc[page_num - 1]
        mat = fitz.Matrix(3, 3)  # 3x zoom for high resolution
        pix = page.get_pixmap(matrix=mat)
        output_path = os.path.join(output_dir, f"교과서_p{page_num}.png")
        pix.save(output_path)
        print(f"Saved: {output_path}")

if __name__ == '__main__':
    # Extract pages 12 to 27 for Unit 1, Lesson 1
    extract_pages("[사회]6_1_교과서.pdf", "assets/pages", range(12, 28))
