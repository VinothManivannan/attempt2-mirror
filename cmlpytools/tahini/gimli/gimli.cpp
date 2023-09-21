/***************************************************************************************************
 * @copyright Copyright (C) 2022 Cambridge Mechatronics Ltd. All rights reserved.
 * @par Disclaimer
 * This software is supplied by Cambridge Mechatronics Ltd. (CML) and is only intended for use with
 * CML products. No other uses are authorised. This software is owned by Cambridge Mechatronics
 * Ltd. and is protected under all applicable laws, including copyright laws.
 **************************************************************************************************/

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <list>
#include <regex>
#include <set>
#include <llvm/DebugInfo/DWARF/DWARFContext.h>
#include <llvm/Support/InitLLVM.h>
#include <llvm/Support/JSON.h>
#include <llvm/Support/MemoryBuffer.h>

using namespace std;
using namespace llvm;
using namespace llvm::object;

class BlockCommentDecoder
{
private:
    // Mapping from file path -> file lines
    std::map<string, unique_ptr<vector<string>>> cache;

    /**
     * @brief  Obtain reference to a file contents organised as an array of lines, cache on first request
     * @param  path The absolute file path
     * @return Array of lines, empty if file could not be found
     */
    const vector<string> &fetchFile(string path)
    {
        vector<string> *file;

        std::map<string, unique_ptr<vector<string>>>::iterator it = cache.find(path);

        // In the cache?
        if (it != cache.end())
        {
            // Yes, iterator is pair<key, value>, so take the value!
            file = it->second.get();
        }
        else
        {
            file = new vector<string>();

            // Push the file path as the 0'th line as line numbers are 1-based
            string line = path;
            ifstream stream = ifstream(path);
            do
            {
                file->push_back(line);
            } while (std::getline(stream, line));

            // Now cache it
            cache[path] = unique_ptr<vector<string>>(file);
        }

        return *file;
    }

    /**
     * @brief  Test if line contains nothing but ( spaces|tabs )
     * @param  line String representation (assumed UTF-8) of the line
     * @return True or false
     */
    inline bool isBlank(string line) { return regex_match(line, std::regex("[ \t]*")); }

    /**
     * @brief  Test if line matches ( spaces|tabs + '/' + '*' + [any[...]] )
     * @param  line String representation (assumed UTF-8) of the line
     * @return True or false
     */
    inline bool isBlockCommentBegin(string line) { return regex_match(line, std::regex("[ \t]*\\/\\*.*")); }

    /**
     * @brief  Test if line matches ( [any[...]] + '*' + '/' + spaces|tabs )
     * @param  line String representation (assumed UTF-8) of the line
     * @return True or false
     */
    inline bool isBlockCommentEnd(string line) { return regex_match(line, std::regex(".*\\*/\\/[ \t]*")); }

    /**
     * @brief  Test if line begins with ( spaces|tabs + '/' + '/' + spaces|tabs + "@regmap" + spaces|tabs )
     * @param  line String representation (assumed UTF-8) of the line
     * @return True or false
     */
    inline bool containsRegmapAttribute(string line) { return regex_match(line, std::regex("[ \t]*\\/\\/[ \t]*@regmap[ \t]*.*")); }

    /**
     * @brief  Remove leading ( spaces|tabs + '/' + '/' + spaces|tabs + "@regmap" + spaces|tabs )
     * @param  line String representation (assumed UTF-8) of the line
     * @return Remainder of line
     */
    inline string extractRegmapAttribute(string line) { return regex_replace(line, std::regex("[ \t]*\\/\\/[ \t]*@regmap[ \t]*"), ""); }

    /**
     * @brief  Split into array of tokens
     * @param  line String representation (assumed UTF-8) of the line
     * @param  re Regular expression for the separator
     * @return Array of string tokens
     */
    inline vector<string> tokenizeRegmapAttribute(string line, const std::regex re)
    {
        regex double_quotes("\"\"");
        if (regex_search(line, double_quotes))
        {
            errs() << "A double \" has been written in " << line << "\n";
            exit(EXIT_FAILURE);
        }
        return vector<string>{sregex_token_iterator(line.begin(), line.end(), re, -1), sregex_token_iterator()};
    }

    /**
     * @brief  Split into array of tokens, separated by ( spaces|tabs + ':' + spaces|tabs )
     * @param  line String representation (assumed UTF-8) of the line
     * @return Array of string tokens
     */
    inline vector<string> tokenizeRegmapAttribute(string line) { return tokenizeRegmapAttribute(line, std::regex("[ \t]*:[ \t]*")); }

    /**
     * @brief  Decode 'C/C++' single-line comments, and output any '<key>' '<value>' attibutes
     * @param  jos Reference to a JSON output stream, all decoded output sent here
     * @param  file Reference to array of file lines
     * @param  line_number Number of [declaring] line
     */
    void decode(json::OStream &jos, const vector<string> &file, int64_t line_number)
    {
        list<string> comment;

        if (line_number < file.size())
        {

            bool within_block_comment = false;

            // Collect @regmap attributes in "C/C++" single-line comments
            while (line_number-- > 0)
            {
                const string line = file[line_number];

                if (isBlank(line))
                {
                    // No action, blank line
                }
                else if (within_block_comment && isBlockCommentEnd(line))
                {
                    // No action
                    within_block_comment = false;
                }
                else if (within_block_comment)
                {
                    // No action
                }
                else if (isBlockCommentBegin(line))
                {
                    // No action
                    within_block_comment = true;
                }
                else if (containsRegmapAttribute(line))
                {
                    // Action, cache line in reverse order
                    comment.push_front(line);
                }
                else
                {
                    // Action, matched comment open
                    break;
                }
            }
        }

        for (auto line : comment)
        {
            // If this is a regmap attribute, we'll have 2 tokens [ name, value ]

            auto tokens = tokenizeRegmapAttribute(extractRegmapAttribute(line));

            if (tokens.size() < 2)
            {
                errs() << "Regmap attribute " << tokens[0] << " is incomplete"
                       << "\n";
                exit(EXIT_FAILURE);
            }
            else
            {
                if (tokens.size() > 2)
                {
                    /* Combine strings accidentally separated due to colons */
                    for (int i = 2; i < tokens.size(); i++)
                    {
                        tokens[1] += ":" + tokens[i];
                    }
                }
                if (auto value = json::parse(tokens[1]))
                {
                    Error error = value.takeError();
                    if (error)
                    {
                        errs() << "Could not parse comment, " << toString(std::move(error)) << "\n";
                        exit(EXIT_FAILURE);
                    }
                    jos.attribute(tokens[0], value.get());
                }
            }
        }
    }

public:
    /**
     * @brief  Decode a 'C' block comment, and output any '<key>' '<value>' tuples as
     * JSON attibutes.
     *
     * To decode enum constants, use the function `decodeEnum()` instead.
     *
     * @param  jos Reference to a JSON output stream, all decoded output sent here
     * @param  decl_file Name of [declaring] file
     * @param  decl_line Number of [declaring] line
     */
    void decode(json::OStream &jos, string decl_file, int64_t decl_line)
    {
        decode(jos, fetchFile(decl_file), decl_line);
    }

    /**
     * @brief  Decode a 'C' block comment associated to an enum constant, and output any
     * '<key>' '<value>' tuples as JSON attibutes
     * @param  jos Reference to a JSON output stream, all decoded output sent here
     * @param  decl_file Name of [declaring] file that the parent enum class belongs to
     * @param  decl_line Number of [declaring] line of the parent enum class belogs to
     * @param  name Name of the constant or enum member to decode
     */
    void decodeEnum(json::OStream &jos, string decl_file, int64_t decl_line, string name)
    {
        // Enum members are no associated with a file or a line number by LLVM.
        // So some additional work is needed to find the exact declaration line from the
        // enum class declaration file and line.
        auto file = fetchFile(decl_file);

        // Test each line until we find the one that contains the constant declaration
        auto regex_pattern = "[ \t]*" + name + "([ \t=\\},]|$).*";
        auto regex = std::regex(regex_pattern);
        while (++decl_line < file.size())
        {
            if (regex_match(file[decl_line], regex))
            {
                break;
            }
        }

        if (decl_line < file.size())
        {
            decode(jos, file, decl_line);
        }
    }
};

static BlockCommentDecoder decoder;

/**
 * @brief  Decode a 'C' block comment, and output any '@regmap' '<key>' '<value>' tuples as
 * JSON attributes
 * @param  jos Reference to a JSON output stream, all decoded output sent here
 * @param  die Reference to the DWARF debug-information-entry
 */
void decodeBlockComment(json::OStream &jos, const DWARFDie &die)
{
    if (die.getTag() == dwarf::DW_TAG_enumerator)
    {
        auto parent = die.getParent();
        decoder.decodeEnum(jos, parent.getDeclFile(DILineInfoSpecifier::FileLineInfoKind::AbsoluteFilePath), parent.getDeclLine(), die.getShortName());
    }
    else
    {
        decoder.decode(jos, die.getDeclFile(DILineInfoSpecifier::FileLineInfoKind::AbsoluteFilePath), die.getDeclLine());
    }
}

/**
 * @brief  Decode a variable with 'C' enum type
 * @param  jos Reference to a JSON output stream, all decoded output sent here
 * @param  die Reference to the DWARF debug-information-entry
 */
static void decodeEnum(json::OStream &jos, const DWARFDie &die)
{
    DWARFDie enumeration_type;

    // Traverse the variable's type chain ...
    for (DWARFDie type = die.getAttributeValueAsReferencedDie(dwarf::DW_AT_type);
         type;
         type = type.getAttributeValueAsReferencedDie(dwarf::DW_AT_type))
    {

        switch (type.getTag())
        {
        case dwarf::DW_TAG_enumeration_type:
            enumeration_type = type;
            break;
        default:
            // Ignore
            break;
        }
    }

    if (enumeration_type)
    {
        jos.objectBegin();

        // Decode enum-specifier identifier
        jos.attribute("name", die.getShortName());

        // Decode @regmap comments - attached to variable type
        decodeBlockComment(jos, enumeration_type);

        // Decode @regmap comments - attached to variable
        decodeBlockComment(jos, die);

        jos.attributeBegin("enumerators");
        jos.arrayBegin();

        // Iterate over enumeration 'type' DWARF debug-information-entry list
        for (auto child : enumeration_type.children())
        {
            // Is this an enumerator?
            if (child.getTag() == dwarf::DW_TAG_enumerator)
            {

                auto value = child.find(dwarf::DW_AT_const_value);
                if (value)
                {
                    jos.objectBegin();

                    // Decode enumerator identifier
                    jos.attribute("name", child.getShortName());

                    // Decode enumerator constant
                    jos.attribute("value", dwarf::toUnsigned(value));

                    // Decode @regmap comments - attached to enumerator
                    decodeBlockComment(jos, child);

                    jos.objectEnd();
                }
            }
        }

        jos.arrayEnd();
        jos.attributeEnd();

        jos.objectEnd();
    }
}

/**
 * @brief  Decode a variable with 'C' base, struct or union type
 * @param  jos Reference to a JSON output stream, all decoded output sent here
 * @param  die Reference to the DWARF debug-information-entry
 * @param  depth Depth of parent in JSON object tree, 0 = uppermost
 */
static void decodeBaseStructUnion(json::OStream &jos, const DWARFDie &die, unsigned int depth = 0)
{
    DWARFDie array_type;
    DWARFDie base_type;
    DWARFDie structure_type;
    DWARFDie union_type;

    DWARFDie base_struct_union_type;

    // Traverse the variable's type chain ...
    for (DWARFDie type = die.getAttributeValueAsReferencedDie(dwarf::DW_AT_type);
         type;
         type = type.getAttributeValueAsReferencedDie(dwarf::DW_AT_type))
    {

        switch (type.getTag())
        {
        case dwarf::DW_TAG_array_type:
            array_type = type;
            break;
        case dwarf::DW_TAG_base_type:
            base_struct_union_type = base_type = type;
            break;
        case dwarf::DW_TAG_structure_type:
            base_struct_union_type = structure_type = type;
            break;
        case dwarf::DW_TAG_union_type:
            base_struct_union_type = union_type = type;
            break;
        default:
            // Ignore
            break;
        }
    }

    // Does the variable have base, struct or union type?
    if (base_struct_union_type)
    {

        jos.objectBegin();

        // Decode type
        if (base_type)
        {
            jos.attribute("type", base_type.getShortName());
        }
        else if (structure_type)
        {
            jos.attribute("type", "struct");
        }
        else if (union_type)
        {
            jos.attribute("type", "union");
        }

        // Decode name
        {
            jos.attribute("name", die.getShortName());
        }

        // Decode @regmap comments - attached to variable type
        decodeBlockComment(jos, base_struct_union_type);

        // Decode @regmap comments - attached to variable
        decodeBlockComment(jos, die);

        // Decode array?
        if (array_type)
        {

            DWARFDie subrange_type;

            // Traverse the array_type's children ...
            for (auto type : array_type.children())
            {

                switch (type.getTag())
                {
                case dwarf::DW_TAG_subrange_type:
                    subrange_type = type;
                    break;
                default:
                    // Ignore
                    break;
                }
            }

            uint64_t value = 0;

            // Determine array count?
            if (subrange_type)
            {

                auto count = subrange_type.find(dwarf::DW_AT_count);
                auto upper_bound = subrange_type.find(dwarf::DW_AT_upper_bound);

                // XXX - we can assume 'C' 0-based array indexing

                if (count)
                {
                    // XXX - attempt to convert to non-zero value
                    value = dwarf::toUnsigned(count, 0);
                }
                else if (upper_bound)
                {
                    // XXX - attempt to convert to non-zero value
                    value = dwarf::toUnsigned(upper_bound, -1) + 1;
                }
            }

            if (value == 0)
            {
                errs() << "error: could not determine array count"
                       << "\n";
                exit(EXIT_FAILURE);
            }

            jos.attribute("array_count", value);
        }

        // Decode [byte] offset?
        if (depth > 0)
        {
            /*
             * TODO - this needs more work, CHESSCC.exe output fails here and
             * bitfields want something else too.
             * Plus, it is just a crap bit of code.
             */
            auto value = die.find(dwarf::DW_AT_data_member_location);
            if (value)
            {
                jos.attribute("byte_offset", dwarf::toUnsigned(value));
            }
        }

        // Decode [byte] size
        {
            auto value = base_struct_union_type.find(dwarf::DW_AT_byte_size);
            if (value)
            {
                jos.attribute("byte_size", dwarf::toUnsigned(value));
            }
        }

        // Decode bit offset?
        if (base_type)
        {
            auto value = die.find(dwarf::DW_AT_bit_offset);
            if (value)
            {
                jos.attribute("bit_offset", dwarf::toUnsigned(value));
            }
        }

        // Decode bit size?
        if (base_type)
        {
            auto value = die.find(dwarf::DW_AT_bit_size);
            if (value)
            {
                jos.attribute("bit_size", dwarf::toUnsigned(value));
            }
        }

        // Decode struct or union members?
        if (structure_type || union_type)
        {
            jos.attributeBegin("members");
            jos.arrayBegin();

            // Iterate over 'child' DWARF debug-information-entry list
            for (auto child : base_struct_union_type.children())
            {
                // Is this a struct or union member?
                if (child.getTag() == dwarf::DW_TAG_member)
                {
                    decodeBaseStructUnion(jos, child, depth + 1);
                }
            }

            jos.arrayEnd();
            jos.attributeEnd();
        }

        jos.objectEnd();
    }
}

/**
 * @brief  Conventional entry point for the program
 * @param  argc Number of arguments
 * @param  argv Array of 'C' strings
 * @return EXIT_SUCCESS or EXIT_FAILURE
 */
int main(int argc, char **argv)
{
    // Explanation of InitLLVM's purpose taken from 'InitLLVM.h'

    // The main() functions in typical LLVM tools start with InitLLVM which does
    // the following one-time initializations:
    //
    //  1. Setting up a signal handler so that pretty stack trace is printed out
    //     if a process crashes. A signal handler that exits when a failed write to
    //     a pipe occurs may optionally be installed: this is on-by-default.
    //
    //  2. Set up the global new-handler which is called when a memory allocation
    //     attempt fails.
    //
    //  3. If running on Windows, obtain command line arguments using a
    //     multibyte character-aware API and convert arguments into UTF-8
    //     encoding, so that you can assume that command line arguments are
    //     always encoded in UTF-8 on any platform.
    //
    // InitLLVM calls llvm_shutdown() on destruction, which cleans up
    // ManagedStatic objects.

    InitLLVM library(argc, argv);

    if (argc < 2)
    {
        errs() << "\n";
        errs() << "Usage:"
               << "\n";
        errs() << "-\tgimli <firmware-binary-path>"
               << "\n";
        errs() << "-\tgimli <firmware-binary-path> <compile-unit-name.c>"
               << "\n";
        errs() << "-\tgimli <firmware-binary-path> <compile-unit-name.c> ..."
               << "\n";
        errs() << "\n";
        errs() << "Notes:"
               << "\n";
        errs() << "-\tThe <compile-unit-name.c> is optional, it is derived from the <firmware-binary-path> if not specified."
               << "\n";
        errs() << "-\tThe ... represents 1 or more additional <compile-unit-name.c>."
               << "\n";
        errs() << "-\tGimli outputs error messages to `stderr`."
               << "\n";
        errs() << "-\tGimli outputs 'Input JSON File' formatted information to `stdout`."
               << "\n";
        errs() << "\n";
        exit(EXIT_FAILURE);
    }

    auto path = argv[1];

    set<string> compile_unit_names;

    for (int i = 2; i < argc; i++)
    {
        compile_unit_names.emplace(argv[i]);
    }

#if 1
    if (compile_unit_names.empty())
    {
        /*
         * XXX - we assume that the firmware binary (*.elf, *.exe, *xexe, etc) has a
         * similarily named 'main' compilation unit.
         */
        compile_unit_names.emplace(filesystem::path(argv[1]).filename().replace_extension(".c").string());
    }
#endif

    // Attempt to buffer file
    ErrorOr<std::unique_ptr<MemoryBuffer>> file_or_error = MemoryBuffer::getFile(path);

    // Verify we have a valid file
    {
        Error error = errorCodeToError(file_or_error.getError());
        if (error)
        {
            errs() << path << ": " << toString(std::move(error)) << "\n";
            exit(EXIT_FAILURE);
        }
    }

    // Attempt to create binary (i.e. treat file as an ELF binary)
    Expected<std::unique_ptr<Binary>> binary_or_error = object::createBinary(*file_or_error.get());

    // Verify we have a valid binary
    {
        Error error = binary_or_error.takeError();
        if (error)
        {
            errs() << path << ": " << toString(std::move(error)) << "\n";
            exit(EXIT_FAILURE);
        }
    }

    // Attempt to obtain an object file
    auto *object_or_nullptr = dyn_cast<ObjectFile>(binary_or_error->get());

    // Verify we have a valid object file
    if (object_or_nullptr == nullptr)
    {
        errs() << "Could not obtain object file from " << path << "\n";
        exit(EXIT_FAILURE);
    }

    // Create DWARF context for the 'firmware' object
    auto context = DWARFContext::create(*object_or_nullptr);

    vector<DWARFDie> dwarf_enums;
    vector<DWARFDie> dwarf_regmap;

    for (std::unique_ptr<DWARFUnit> &unit : context->compile_units())
    {
        const DWARFDie &die = unit->getUnitDIE(false);

        // Is a compile unit of interest?
        if (compile_unit_names.empty() || (compile_unit_names.find(filesystem::path(die.getShortName()).filename().string()) != compile_unit_names.end()))
        {

            // Decode enum type'd variables...
            for (DWARFDie child = die.getFirstChild(); child; child = child.getSibling())
            {
                if (child.getTag() == dwarf::DW_TAG_variable)
                {

                    bool has_enumeration_type = false;

                    // Have a peek at the variable's type to determine if this is a 'C' enum or not
                    for (DWARFDie type = child.getAttributeValueAsReferencedDie(dwarf::DW_AT_type);
                         type;
                         type = type.getAttributeValueAsReferencedDie(dwarf::DW_AT_type))
                    {

                        if (type.getTag() == dwarf::DW_TAG_enumeration_type)
                        {
                            has_enumeration_type = true;
                            break;
                        }
                    }

                    // Where is it to be cached?
                    if (has_enumeration_type)
                    {
                        dwarf_enums.push_back(child);
                    }
                    else
                    {
                        dwarf_regmap.push_back(child);
                    }
                }
            }
        }
    }

    // Create JSON output-stream - compact output (indent=0), readable (indent>0)
    auto jos = json::OStream(outs(), 2);

    jos.objectBegin();

    // Output the 'regmap' JSON array
    {
        jos.attributeBegin("regmap");
        jos.arrayBegin();

        for (auto die : dwarf_regmap)
        {
            decodeBaseStructUnion(jos, die);
        }

        jos.arrayEnd();
        jos.attributeEnd();
    }

    // Output the 'enums' JSON array
    {
        jos.attributeBegin("enums");
        jos.arrayBegin();

        for (auto die : dwarf_enums)
        {
            decodeEnum(jos, die);
        }

        jos.arrayEnd();
        jos.attributeEnd();
    }

    jos.objectEnd();

    return EXIT_SUCCESS;
}
