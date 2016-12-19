import pyexiv2


def writeEXIF(jpgFile, val):
    metadata = pyexiv2.ImageMetadata(jpgFile) 
    metadata.read()

    #print metadata.exif_keys
    exif_uc = 'Exif.Photo.UserComment'
    metadata[exif_uc] = pyexiv2.ExifTag(exif_uc, val)
    metadata.write()
    return True


    
#def main():
#    writeEXIF('img2.jpg', 'area-1')
  
    
#if __name__ == '__main__':
#    main()
