import os
from tahini_add_json_info import CombineJsonFiles

if __name__ == "__main__":
    input_path1 = os.path.join(os.getcwd(), "add_info_to_reg.json")
    input_path2 = os.path.join(os.getcwd(), "test_input_json_to_combine.json")
    CombineJsonFiles.combine_json_files(input_path2, input_path1)
