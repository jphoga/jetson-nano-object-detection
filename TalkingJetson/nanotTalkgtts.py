import os
from gtts  import gTTS
myText='Get ready Player one. The play will be rough. Are you ready to rumble.'
myOutput=gTTS(text=myText, lang='en', slow=False)
myOutput.save('talk.mp3')
os.system('mpg123 talk.mp3')