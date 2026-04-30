import pdfplumber

with pdfplumber.open('artifacts/SOD00093649.pdf') as pdf:
    print('Pages:', len(pdf.pages))
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ''
        print(f'PAGE {i+1} ({len(text)} chars):')
        print(text[:3000])
        print('---TABLES---')
        tables = page.extract_tables()
        print('table count:', len(tables))
        for t in tables:
            for row in t:
                print(row)
        print('=====')
