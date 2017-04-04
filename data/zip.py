import zipfile

def unzip(filename, dir):
    zip = zipfile.ZipFile(filename, 'r')
    zip.extractall(dir)
    zip.close()
    print("Done unzipping.")

