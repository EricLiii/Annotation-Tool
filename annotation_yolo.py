import os 
import copy

class AnnotationYOLO():
    def __init__(self):
        pass

    def read_label(self, label_path):      
        if os.path.isfile(label_path):  
            with open(label_path, "r") as f:
                saved_label = []
                lines = f.readlines()
                for i in range(len(lines)):
                    line = lines[i].split()
                    one_list = [int(line[0])]
                    coor_list = []
                    for j in range(1, len(line)):                   
                        coor_list.append(float(line[j]))
                    one_list.append(coor_list)
                    saved_label.append(one_list)
            return saved_label
        else:
            print("There is no label file!")

    def write_label(self, saved_label, label_path):
        saved_rects_copy = copy.deepcopy(saved_label)
        with open(label_path, "w") as f:
            lines = []
            for item in saved_rects_copy:
                line = []
                line.append(str(item[0]))
                for i in range(len(item[1])):
                    line.append("%.5f"%item[1][i])
                line = " ".join(line)
                lines.append(line + "\n")
            for line_ in lines:
                f.write(line_)
            #TODO: does the last "\n" have bad effect on training?
