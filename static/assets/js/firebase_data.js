const database = firebase.database();
const messageRef = database.ref();

messageRef.on("value", function (snapshot) {
    // console.log(snapshot.val());
    token = snapshot.val().AuthenKey;
}, function (error) {
    console.log("Error: " + error.code);
});

