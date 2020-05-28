#from keras.models import load_model
import cv2
from matplotlib import pyplot as plt
import numpy as np
import os 
from tensorflow.keras.models import load_model
import uuid
import platform
#from keras.preprocessing.image import ImageDataGenerator
#from sklearn.metrics import classification_report, confusion_matrix

#def SingleImageInference():
# No queremos que se cargue el modelo cada vez que se hace la inferencia
def singleInference(img,model,k):
    if platform.system() == "Windows":
        dash = "\\"
    else:
        dash = "/"
    # Establish main path for files # <-- Final GUI change
    path = dash.join(os.path.realpath(__file__).split(dash)[:-1]) + dash

    #model.compile(loss='categorical_crossentropy',optimizer='rmsprop',metrics=['accuracy'])
    valid_directory =path + "classes"
    w= [x[0] for x in os.walk(valid_directory)]
    del w[0]

    f = [x.replace(valid_directory, '') for x in w]
    #print(f)
    img = cv2.imread(img)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    #plt.imshow(img)
    img = cv2.resize(img,(200,200))

    img = np.reshape(img,[1,200,200,3])/255.0

    classes = model.predict_classes(img)

    whut = model.predict(img)
    win = classes[0]

    flat = whut.flatten()
    flat.sort()

    flat2_1= np.where(flat[-1]==whut)
    x1,y1 = flat2_1
    y1_1 = y1.astype(int)
    y1_1 = int(y1_1)


    flat2_2= np.where(flat[-2]==whut)
    x2,y2 = flat2_2
    y1_2 = y2.astype(int)
    y1_2 = int(y1_2)


    flat2_3= np.where(flat[-3]==whut)
    x3,y3 = flat2_3
    y1_3 = y3.astype(int)
    y1_3 = int(y1_3)


    F = [f[y1_1],f[y1_2],f[y1_3]]
    #print(F)
    flat0 = [flat[-i]*100 for i in range(1,4) ]
   
    """
    f[y1_1] : nombre 1
    f[y1_2] : nombre 2
    f[y1_3] : nombre 3
    """

    font1 = {'color':  'green','weight': 'normal','size': 16}
    font2 = {'color':  'red','weight': 'normal','size': 16}
    

    LstReturn = [ "{0} {1:.3f}%".format(F[i], flat0[i]) for i in range(0,3)]
    #print(LstReturn)
    plt.xticks([])
    plt.yticks([])
    plt.xlabel(LstReturn[0]+" "+LstReturn[1]+" "+LstReturn[2])
    
    Uid = uuid.uuid1()
    
    image_name =str(Uid)+'_predict_img_'+str(k)
    plt.savefig(image_name)
    #plt.show()  
    F = [str.replace("\\", "") for str in F]
    #print(F)
    return F, flat0, f


