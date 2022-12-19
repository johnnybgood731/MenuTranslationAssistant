var recognition;

function startSpeech() {
  // check if the browser supports the Web Speech API
  if ('webkitSpeechRecognition' in window) {
    // create a new SpeechRecognition object
    recognition = new window.webkitSpeechRecognition();

    // set the language and start the recognition
    recognition.lang = 'en-US';
    recognition.start();

    // listen for the result event and update the text input
    recognition.addEventListener('result', function(event) {
      document.getElementById("text-prompt").value = event.result[0][0].transcript;
    });
  }
  else {
  console.log("Speech Recognition Not Available")
}
}