import pandas as pd
import re

d= {"avocado": "AGUACATE SUPREMO", "banana":"PLATANO", 
    "carrot": "ZANAHORIA","coriander":"HEB CILANTRO MANOJO",
    "corn": "ELOTE BLANCO", "cucumber": "PEPINO FRESCO" ,
    "goldenapple": "MANZANA GOLDEN IMP SUPREMA", "lime": "LIMON  AGRIO SUPREMO",
    "mango":"MANGO ATAULFO SUPREMO", "onion":"CEBOLLA BCA LIMPIA",
    "orange":"NARANJA  SUPREMA",  "orangepepper":"PIMIENTO NARANJA",
    "pineapple": "PINA MIEL SUPREMA PZA", "potato":"PAPA BLANCA", 
    "purpleonion":"CEBOLLA MORADA", "redapple": "MANZANA RED DELICIOUS IMP SUPREMA",
    "redpepper":"PIMIENTO ROJO", "serrano": "CHILE SERRANO", 
    "tomato": "TOMATE BOLA SUPREMO", "zucchini":"CALABACITA",
    "aguacate": "AGUACATE SUPREMO", "platano":"PLATANO", 
    "zanahoria": "ZANAHORIA","cilantro":"HEB CILANTRO MANOJO",
    "elote_blanco": "ELOTE BLANCO", "pepino": "PEPINO FRESCO" ,
    "manzana_golden": "MANZANA GOLDEN IMP SUPREMA", "limon": "LIMON  AGRIO SUPREMO",
    "mango":"MANGO ATAULFO SUPREMO", "cebolla":"CEBOLLA BCA LIMPIA",
    "naranja":"NARANJA  SUPREMA", 
    "papa":"PAPA BLANCA", 
    "redapple": "MANZANA RED DELICIOUS IMP SUPREMA", 
    "tomate_bola": "TOMATE BOLA SUPREMO", "calabacita":"CALABACITA",
    "melon":"MELON SUPREMO","tomate_huaje":"TOMATE HUAJE SUPREMO","papaya":"PAPAYA MARADOL",
    "jicama":"JICAMA GDE","fresa":"FRESA 1 LB","brocoli":"BROCOLI CORONAS"}


F = ["avocado", "orange", "onion"]

#print(d.get(d[F[0]])
#print(d[F[0]])

df = pd.read_csv("MayoHEB_1.csv")
df = pd.DataFrame(df)

df1 = df['Producto'].to_list()
df1 = [product.strip() for product in df1]
df1 = [product.replace("  ", " ") for product in df1]
# strip trailing and leading whitespaces

#print(df1)
df2 = df["PLU"].to_list()
for element in df2:
    element = str(element)
#print(df2)
#df2 = [product.strip() for product in df2]
# remove traiing and leading whitespaces

products= dict(zip(df1,df2))
#print(products.get("carrot"))

"""print (d.get("avocado"))
x= d.get("avocado")
print(products.get(x))"""