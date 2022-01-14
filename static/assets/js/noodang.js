//responsiveVoice.setDefaultVoice("Thai Female");	  
//responsiveVoice.speak("Touch Smart Office Voice Control Online","Thai Female", {pitch: 1.1});	


setTimeout(function () {
  startButton(event);
}, 500);

var final_transcript = '';
var finalTranscripts = '';
var recognizing = false;
var ignore_onend;
var activate = false;

// var message = document.getElementById('message');
// var resultmessage = document.getElementById('resultmessage');

if (!('webkitSpeechRecognition' in window)) {
  upgrade();
} else {
  var recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onstart = function () {
    recognizing = true;
  };

  recognition.onerror = function (event) { };

  recognition.onend = function () {
    recognizing = false;
    if (ignore_onend) {
      return;
    }

    if (!final_transcript) {
      var bot = finalTranscripts;
      // console.log(bot);

      if (bot != "") {
        if (bot == "สวัสดีหนูแดง") {
          activate = true;
          speech_new("สวัสดีคะ มีอะไรให้หนูแดงรับใช้คะ");
          startSpeakingAction();
          //responsiveVoice.speak("สวัสดีคะ มีอะไรให้หนูแดงรับใช้คะ", "Thai Female", {pitch: 1.1});

        } else if (bot == "ขอบคุณ") {
          if (activate != false) {
            activate = false;
            speech_new("ยินดีค่ะ ครั้งหน้าเรียกใช้หนูแดงได้นะคะ");
            stopSpeakingAction();
            // 		responsiveVoice.speak("ยินดีค่ะ ครั้งหน้าเรียกใช้หนูแดงได้นะคะ", "Thai Female", {pitch: 1.1});

          };
        }
        //keycompare(bot);
        if (activate) {
          console.log(bot);
          cut(bot);
          // resultmessage.innerHTML = bot;
        }

      }


      setTimeout(function () { startButton(event); }, 10);
      // setTimeout(function () { resultmessage.innerHTML = "หนูแดงกำลังรอรับคำสั่งอยู่นะคะ"; }, 3000);
      return;
    }

  };

  recognition.onresult = function (event) {

    var interimTranscripts = '';
    for (var i = event.resultIndex; i < event.results.length; i++) {
      var transcript = event.results[i][0].transcript;
      //transcript.replace("\n", "<br>");
      if (event.results[i].isFinal) {
        finalTranscripts = transcript;
      } else {
        interimTranscripts = transcript;
      }
    }
    // console.log(interimTranscripts);
    
    // $('#message').html(interimTranscripts);
    //message.innerHTML = interimTranscripts;
  };
}


function startButton(event) {
  if (recognizing) {
    recognition.stop();
    return;
  } else {
    // speakingAction();
    //stopSpeakBtnAction();
    final_transcript = '';
    finalTranscripts = '';
    recognition.lang = 'th-TH';
    recognition.start();
    ignore_onend = false;
  }
}

