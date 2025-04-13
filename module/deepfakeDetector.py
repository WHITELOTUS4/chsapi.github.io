import os
import Preprocessor
from module import dfd_p1
from module import dfd_p2

module_dir = os.path.dirname(__file__)
if os.path.exists(os.path.join(module_dir, 'temp.py')):
    from module import temp as dfd_p1

def hard_voting(voters):
    real = 0
    fake = 0
    total_accuracy = 0
    for i in range(0, len(voters), 1):
        if voters[i]["class"] == 'Real':
            real += 1
        elif voters[i]["class"] == 'Fake':
            fake += 1
        total_accuracy += voters[i]["accuracy"]
    accuracy = round((total_accuracy / len(voters)), 2)
    winer = 'Real' if real > fake else 'Fake'
    return {"class": winer, "accuracy": accuracy}

def detect_image(input_list, no_of_model):
    if no_of_model == 'single':
        src = dfd_p1.detect_image(input_list)
        Preprocessor.single_img_bin.clear()
        return src
    elif no_of_model == 'all':
        if(input_list[0]=='load'):
            input_list[0] = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin.copy())
        p1 = dfd_p1.detect_image(input_list)
        p2 = dfd_p2.detect_image(input_list)
        src = Preprocessor.MutableDict(p1).insert("responce_tree", {"prototype_1": p1, "prototype_2": p2})
        Preprocessor.single_img_bin.clear()
        return src
