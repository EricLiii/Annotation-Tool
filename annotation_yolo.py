import os 

class AnnotationYOLO():
    def __init__(self):
        pass

    def read_label(self):
        pass

    def write_label(self, saved_label, label_path):
        with open(label_path, "w") as f:
            lines = []
            for item in saved_label:
                for i in range(len(item)):
                    item[i] = str(item[i])
                line = " ".join(item)
                lines.append(line + "\n")
            for line_ in lines:
                f.write(line_)
            #TODO: does the last "\n" have bad effect on training?
