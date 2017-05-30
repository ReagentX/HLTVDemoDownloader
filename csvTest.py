import csv
fields = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
with open(r'name.csv', 'a', encoding='utf-8') as f:
    print(f)
    writer = csv.writer(f)
    for i in range(0, len(fields)):
        writer.writerow(fields[i])
