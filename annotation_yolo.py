import os 
import copy

class AnnotationYOLO():
    def __init__(self):
        pass

    def read_label(self, label_path):        
        with open(label_path, "r") as f:
            saved_label = []
            lines = f.readlines()
            for i in range(len(lines)):
                line = lines[i].split()
                for j in range(len(line)):
                    line[j] = float(line[j])
                saved_label.append(line)
        return saved_label

    def write_label(self, saved_label, label_path):
        saved_rects_copy = copy.deepcopy(saved_label)
        with open(label_path, "w") as f:
            lines = []
            for item in saved_rects_copy:
                for i in range(len(item)):
                    item[i] = str(item[i])
                line = " ".join(item)
                lines.append(line + "\n")
            for line_ in lines:
                f.write(line_)
            #TODO: does the last "\n" have bad effect on training?
