from __future__ import annotations

from pathlib import Path

from Classes.ExtractedFileStatements import ExtractedFileStatements
from Classes.Symbol.Symbol import Symbol
from Classes.Symbol.ClassSymbol import ClassSymbol
from Classes.Symbol.FunctionSymbol import FunctionSymbol
from Classes.Symbol.MacroSymbol import MacroSymbol
from Classes.Symbol.StructSymbol import StructSymbol
from Classes.Symbol.TypedefSymbol import TypedefSymbol
from regexTools.getImplementation import get_c_function_imp, get_cpp_class_imp, get_struct_imp
from regexTools.getProto import get_macro_proto, get_struct_proto, get_typedef_proto

SYMBOL_TYPES = (
    ClassSymbol,
    FunctionSymbol,
    MacroSymbol,
    StructSymbol,
    TypedefSymbol,
)


def extract_file_statements(file_text: str) -> ExtractedFileStatements:
    return ExtractedFileStatements(
        classes=get_cpp_class_imp(file_text),
        function_implementations=get_c_function_imp(file_text),
        macros=get_macro_proto(file_text),
        structs=list(dict.fromkeys(get_struct_proto(file_text) + get_struct_imp(file_text))),
        typedefs=get_typedef_proto(file_text),
    )


def collect_symbol_declarations_from_texts(texts_by_path: dict[str, str]) -> dict[type[Symbol], set[str]]:
    declarations_by_type = {symbol_type: set() for symbol_type in SYMBOL_TYPES}
    for file_text in texts_by_path.values():
        for symbol_type in SYMBOL_TYPES:
            declarations_by_type[symbol_type].update(symbol_type.declarations_from_text(file_text))
    return declarations_by_type


def build_symbol_map(
    file_path: str | Path,
    declarations_by_type: dict[type[Symbol], set[str]],
    file_text: str,
) -> dict[str, Symbol]:
    file_path = Path(file_path).expanduser().resolve()
    extracted_file_statements = extract_file_statements(file_text)
    result_map: dict[str, Symbol] = {}
    for symbol_type, declarations in declarations_by_type.items():
        for declaration in declarations:
            implementation = symbol_type.find_matching_implementation(declaration, extracted_file_statements)
            if implementation is None:
                continue
            symbol_name = symbol_type.extract_symbol_name(declaration)
            if symbol_name is None:
                continue
            result_map[symbol_name] = symbol_type(
                declaration=declaration,
                implementation=implementation,
                source=str(file_path),
                recurence={},
            )
    return result_map
