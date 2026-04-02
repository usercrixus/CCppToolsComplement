def get_c_proto(line):

def get_cpp_proto(line):

def get_cpp_class(line):
    #return true if we enter a class, else false + the proto

def traverse_file_system(excludedFolder):
    filesProto = map() # a map of file/proto lile filesProto[filePath].push(proto)
    inclass = False
    # if the file is .c
    filesProto[current].push(get_c_proto(line))
    #  or .cpp
    inclass, proto = get_cpp_class(line)
    filesProto[current].push(proto)
    if not inclass:
        filesProto[current].push(get_cpp_proto(line))
    return filesProto

# it get the path where it should start the traversing + a list of excluded folder
def main():
    excludedFolder = [] # get excluded folder from the args
    filePath = traverse_file_system(excludedFolder)
