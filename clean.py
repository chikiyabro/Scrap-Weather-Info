file_object  = open("grounds_new.txt")
new_file = list()
repeated_names = list()
for i in file_object.readlines():
    if i.split("-->")[:1] not in repeated_names:
        repeated_names.append(i.split("-->")[:1])
        print(i.split("-->")[1:2])
        new_file.append(i)
