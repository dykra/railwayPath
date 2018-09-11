from keras.models import load_model
import logging

logger_format = '%(asctime)-15s s -8s %(message)s'
logging.basicConfig(format=logger_format)


logging.info('Info')

logging.debug("A quirky message only developers care about")
logging.info("Curious users might want to know this")
logging.warning("Something is wrong and any user should be informed")
logging.error("Serious stuff, this is red for a reason")
logging.critical("OH NO everything is on fire")

logging.log(20, 'Poziom 20, to info')

model = load_model('500tys_1mln.h5')
model.summary()

prediction = model.predict(x.values)

    print('First prediction:', prediction[0])


