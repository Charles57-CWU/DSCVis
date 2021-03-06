class DisplayData:
    def __init__(self, dataset, textbox):
        # display class data
        data_info_string = ('Dataset Name: ' + dataset.name +
                            '\n\n' + 'Number of Classes: ' + str(dataset.class_count) +
                            '\n\n' + 'Number of Attributes: ' + str(dataset.attribute_count) +
                            '\n\n' + 'Number of Samples: ' + str(dataset.sample_count))

        # loop through class names
        counter = 1
        for ele in dataset.class_names:
            data_info_string += ('\n\n' + 'Class ' + str(counter) + ': ' + str(ele) +
                                 '\n' + '--Count: ' + str(dataset.count_per_class[counter - 1]))
            counter += 1

        textbox.setText(data_info_string)
