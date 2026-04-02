from pathlib import Path

from protoImplementationMatcher import build_proto_map


def _read_source(file_path):
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


# return a map like myMap[proto] = [{implementation, source, recurence}]
# myMap["MY_MACRO"] = [{"implementation": "MY_MACRO 10", "source": "file/path1.c",
#                       "recurence": [{"source": "file/path1.c", "times": 2}]}]
# myMap["MY_MACRO"] = [{"implementation": "MY_MACRO 10", "source": "file/path1.c",
#                       "recurence": [{"source": "file/path1.c", "times": 2}]},
#                      {"implementation": "MY_MACRO 10", "source": "file/path2.c",
#                       "recurence": [{"source": "file/path2.c", "times": 1}]}]
# then we will put MY_MACRO in the header of file/path1.c, file/path1.h. then include it in all others
def generateHeaderFromC(filePath, proto):
    source_path = Path(filePath).expanduser().resolve()
    source_text = _read_source(source_path)
    return build_proto_map(source_path, proto, source_text)
