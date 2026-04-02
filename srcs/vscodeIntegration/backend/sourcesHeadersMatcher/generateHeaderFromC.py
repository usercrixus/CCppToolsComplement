#return a map like myMap[proto] = {implementation, source, recurence}
# myMap["MY_MACRO"] = {"MY_MACRO", "file/path1.c", 2}
# myMap["MY_MACRO"] = {"MY_MACRO", "file/path2.c", 1}
# then we will put MY_MACRO in the header of file/path1.c, file/path1.h. then include it in all others
def generateHeaderFromC(filePath):
    # TODO LATER
    pass
