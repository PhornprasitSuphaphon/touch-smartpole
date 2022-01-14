var wordcut = require("wordcut");
wordcut.init();

var data_db = {
  data: [
    //พัดลม
    {
      command: ["ระดับน้ำ"],
      Answer: [
        "ยังไม่มีข้อมูลค่ะ",
        "จัดการให้แล้วค่ะ"
      ],
      action: null,
      send: []
    },
    {
      command: ["เปิดพัดลม"],
      Answer: [
        "เปิดพัดลมให้แล้วนะคะ",
        "เปิดให้แล้วค่ะ",
        "ok เปิดแล้วค่ะ",
        "จัดการให้แล้วค่ะ"
      ],
      action: null,
      send: []
    },
    {
      command: ["ปิดพัดลม"],
      Answer: [
        "ปิดพัดลมให้แล้วนะคะ",
        "ปิดให้แล้วค่ะ",
        "ok ปิดแล้วค่ะ",
        "จัดการให้แล้วค่ะ"
      ],
      action: null,
      send: []
    },
    {
      command: ["พูดหลายรอบ", "ฟังไม่รู้เรื่อง", "พูดไม่รู้เรื่อง"],
      Answer: [
        "ขออภัยในความไม่สะดวก",
        "หนูแดงจะปรับปรุงตัวให้ดีกว่านี้ค่ะ",
        "หนูแดงขอไปเรียนใหม่ก่อนนะคะ",
        "หนูแดงขอโทษค่ะ"
      ],
      action: null,
      send: []
    }
  ]
};

function cut(data) {
  // console.log("---------");

  var str_cm = wordcut.cut(data).split("|");
  var str2 = wordcut.cut("").split("|");
  var checkerror = $(str2).not(str_cm).get();

  if (checkerror == 0) {
    for (var i = 0; i < data_db.data.length; i++) {
      for (var cm = 0; cm < data_db.data[i].command.length; cm++) {
        console.log(data_db.data[i].command[cm]);
        var cc = wordcut.cut(data_db.data[i].command[cm]).split("|");
        var check = $(cc).not(str_cm).get();

        if (check.length == 0) {
          if (data_db.data[i].Answer[0] != null) {
            var x = Math.floor(Math.random() * data_db.data[i].Answer.length);
            console.log(data_db.data[i].Answer[x] + "answer");
            speech_new(data_db.data[i].Answer[x]);
            //responsiveVoice.speak(data_db.data[i].Answer[x], "Thai Female", {pitch: 1.1});
          }

          for (var se = 0; se < data_db.data[i].send.length; se++) {
            //alert(data_db.data[i].send[se].deviceId +" "+data_db.data[i].send[se].topic+" "+data_db.data[i].send[se].status+" ") ;
            if (data_db.data[i].action != null) {
              var action = $(this).data("action");
              var fn = window[data_db.data[i].action];
              fn();
            }
          }
        }
      }
    }
  }
}

function speech_new(data) {
  var audio2 = new Audio(
    // "https://code.responsivevoice.org/getvoice.php?t=" + data + "&tl=th&sv=g1&vn=&pitch=0.55&rate=0.5&vol=1&gender=female"
    "http://code.responsivevoice.org/getvoice.php?text=" + data + "&lang=th&engine=g1&name=&pitch=0.5&rate=0.5&volume=1&key=WGciAW2s&gender=female"
  );
  audio2.play();
  // audio2.onended = function() {};
}
