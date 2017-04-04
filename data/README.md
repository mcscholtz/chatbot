1. Get the data: ./get_data.sh
2. Parse the data: python parse.py
3. Create training data by going into each data directory which data you want to use and then copying the *.conv file into a new directory
4. Create another new directory for the training data
5. Run the split_all.py script to create the training data: python split_all.py --f input_data --t 5 --d training_data, where input_data is the directory containing the .conv files and training_data is the directory where the training and testing data will be saved, 5 means 5 percent of the data will be held for testing data
