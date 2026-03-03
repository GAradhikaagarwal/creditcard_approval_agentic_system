import os
import pypdf

folder = r'c:\forked\creditcard and new scheme recommendation'
out_folder = r'c:\forked'
for f in os.listdir(folder):
    if f.endswith('.pdf'):
        try:
            reader = pypdf.PdfReader(os.path.join(folder, f))
            text = ''
            for p in reader.pages:
                if p.extract_text():
                    text += p.extract_text() + '\n'
            
            out_path = os.path.join(out_folder, f.replace('.pdf', '.txt'))
            with open(out_path, 'w', encoding='utf-8') as out_f:
                out_f.write(text)
            print(f"Successfully extracted {f}")
        except Exception as e:
            print(f'Error reading {f}: {e}')
