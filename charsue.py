import chardet

with open('backup_20230507_013208.sql', 'rb') as f:
    result = chardet.detect(f.read())
    print(result['encoding'])