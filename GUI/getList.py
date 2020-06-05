import pandas as pd 

def getListOfItems():
    df = pd.read_csv("AbrilHEB.csv")
    df = pd.DataFrame(df)

    df1 = df['Producto'].to_list()
    df1 = [product.strip() for product in df1]
    df1 = [product.replace("  ", " ") for product in df1]
    df3 = df1
    # strip trailing and leading whitespaces
    df2 = df["PLU"].to_list()
    df2 = [product.strip() for product in df2]
    # remove traiing and leading whitespaces

    concatLen = 0
    # initialize concat space length
    spaceList = [ len(s) for s in df1]
    # measure the length of each string in Product

    concatLen = max(spaceList) +35
    # Each space is accounted for with respect to the maximum length of the longest string
    spaceList = [concatLen-len(s) for s in df1]
    # Number of spaces will be max ( all strs in Product)
    df2Right = [df2[i].rjust(spaceList[i]) for i in range(len(df2))]
    # create the left spaces for the PLUs (justify right accordingly)
    df1 = [df1[i]+df2Right[i] for i in range(len(df2Right))]
    # Products and new justified PLUs unite
    
    
    return df1