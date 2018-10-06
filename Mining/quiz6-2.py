# Q2: 100$ 

input_file = "d:\\data\\csv\\supplier_data.csv"
output_file = "d:\\data\\output\\result2.csv"

with open(input_file, 'r', newline='') as filereader:
    with open(output_file, 'w', newline='') as filewriter:
        header = filereader.readline()
        header = header.strip()
        header_list = header.split(',')
        header_str = ','.join(map(str, header_list))
        filewriter.write(header_str + '\n')
        for  row  in  filereader :  # 모든행은 row에 넣고 돌리기.
            row = row.strip()
            row_list = row.split(',')
            row_list[3] = row_list[3][0] + str(float(row_list[3][1:]) + 100.00)
            if row_list[0] != "Supplier Y":
                row_str = ','.join(map(str, row_list))
            filewriter.write(row_str + '\n')