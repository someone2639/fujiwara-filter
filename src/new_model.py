import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model("fujiwara_trained_model/fujiwarafiltermodel")

def isFujiwara(path):
  print("Hello from the new model!")
  img = tf.keras.utils.load_img(path, target_size=(100, 100))

  img_array = tf.keras.utils.img_to_array(img)
  img_array = tf.expand_dims(img_array, 0)

  predictions = model.predict(img_array)
  score = tf.nn.softmax(predictions[0])

  classes = ("fujiwara","other","pinkhair")
  print("this image is a %s" % classes[np.argmax(score)])
  return classes[np.argmax(score)] == "fujiwara"