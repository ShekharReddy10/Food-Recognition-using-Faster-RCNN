from flask import Flask, flash, redirect, render_template, request

from tensorflow.keras.applications.inception_v3 import preprocess_input
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename
import os
import csv


app = Flask(__name__)
app.config['SECRET_KEY']="Hello"

resnet =load_model('bestmodel_101class.hdf5',compile=False)
print("+"*50, "Model is loaded")

labels = pd.read_csv("labels.txt").values


nutrients = [
    {'name': 'protein', 'value': 0.0},
    {'name': 'calcium', 'value': 0.0},
    {'name': 'fat', 'value': 0.0},
    {'name': 'carbohydrates', 'value': 0.0},
    {'name': 'vitamins', 'value': 0.0}
]

with open('nutrition101.csv', 'r') as file:
    reader = csv.reader(file)
    nutrition_table = dict()
    for i, row in enumerate(reader):
        if i == 0:
            name = ''
            continue
        else:
            name = row[1].strip()
        nutrition_table[name] = [
            {'name': 'protein', 'value': float(row[2])},
            {'name': 'calcium', 'value': float(row[3])},
            {'name': 'fat', 'value': float(row[4])},
            {'name': 'carbohydrates', 'value': float(row[5])},
            {'name': 'vitamins', 'value': float(row[6])}
        ]


@app.route('/')
def index():
	return render_template("index.html")


@app.route("/prediction", methods=["POST"])
def prediction():
	# if 'uploadphoto' not in request.files:
	# 	flash('No File Part')
	# 	return redirect(request.url)
	print('image' not in str(request.files['img']))
	if 'image' not in str(request.files['img']):
		flash('No Image Selected')
		return render_template("prediction.html")
	img = request.files['img']
	basepath = os.path.dirname(__file__)
	file_path = os.path.join(basepath, 'images', secure_filename(img.filename))
	img.save(file_path)
	images=image.load_img(file_path, target_size=(299, 299))
	images = image.img_to_array(images)
	images = np.expand_dims(images, axis=0)
	images = preprocess_input(images)
	pred = resnet.predict(images)
	index = np.argmax(pred)-1
	pred = labels[index]
	nutrients_data=nutrition_table[''.join(list(pred)).lower()]
	protein=''
	calcium=''
	fat=''
	carbohydrates=''
	vitamins=''
	for nut_data in nutrients_data:
		if(nut_data['name']=='protein'):
			protein=nut_data['value']
		elif(nut_data['name']=='calcium'):
			calcium=nut_data['value']
		elif(nut_data['name']=='fat'):
			fat=nut_data['value']
		elif(nut_data['name']=='carbohydrates'):
			carbohydrates=nut_data['value']
		else:
			vitamins=nut_data['value']
	food_img_path=os.path.join('images',img.filename)
	return render_template("prediction.html" , filep=file_path, name=''.join(list(pred)).lower(), data1=protein,data2=calcium,data3=fat,data4=carbohydrates,data5=vitamins)
	


if __name__ == "__main__":
	app.run(debug=True)
