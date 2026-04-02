

def traverse_file_system(startPath, excludedFolderPath):
    #traverse the whole file system from the start point, except the excludedFolderPath
    # if file is .c call generateHeaderFromC.py
    # if file is .cpp call generateHeaderFromCpp.py


# it get the path where it should start the traversing + a list of excluded folder
def main():
    startPath = "/"
    excludedFolderPath = [] # get excluded folder from the args
    traverse_file_system(startPath, excludedFolderPath)