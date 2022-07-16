'use strict';
console.log('Hi this is the on demand script');
// Jeremy's work to error-prove the UI
function isWeekend() {
    let dayOfWeek = (new Date()).getDay();
    return (dayOfWeek == 6) || (dayOfWeek == 0);
}
function isDinnerTime() {
    let hour = (new Date()).getHours();
    // dinner time is from 5pm-8pm
    // do not worry about matches being made exactly at 8pm,
    // will not be valid for matches due to < 30 min availability
    return (17 <= hour) && (hour <= 19);
}
function isLunchTime() {
    let dateTime = new Date();
    let hour = dateTime.getHours();
    let minute = dateTime.getMinutes();
    // lunch time is from 11:30am-2pm
    // do not worry about matches being made exactly at 2pm,
    // will not be valid for matches due to < 30 min availability

    if (isWeekend()) // weekend lunch hours are 10AM - 2PM
        return (10 <= hour) && (hour <= 13);
    else // weekday lunch hours, 11:30am -- 2pm
        return (12 <= hour || (11 == hour && minute >= 30)) && (hour <= 13);
}
function updateEndTime() {
    let endTimeEL = document.getElementById('endTimeButton')
    let dateTime = new Date();
    if (isDinnerTime())
        endTimeEL.setAttribute('max', '20:00')
    else if (isLunchTime())
        endTimeEL.setAttribute('max', '14:00');
}
$('document').ready(updateEndTime);




let dHallButtons = document.getElementsByClassName('dHallType')
let activeDhall = "";

let anyDhallButton = document.getElementById('anyDhall');
// is anyDhall active
let isAnyActive = false;

for (let i = 0; i < dHallButtons.length; i++) {
    let btn = dHallButtons[i];
    btn.addEventListener('click',
        function () {
            activeDhall = btn.id;
            btn.style.backgroundColor = "#ff9f46";


            for (let j = 0; j < dHallButtons.length; j++)
                if (dHallButtons[j].id != btn.id) {
                    dHallButtons[j].style.backgroundColor = "";

                }
        });
}

//

let submitButtonForm = document.getElementById("submitButtonForm");



// update url to contain proper match request information
function updateUrl() {
    console.log('called updateurl')

    let url = "/submitrequest"
    let endTime = document.getElementById("endTimeButton").value;


    let activeMeal = "";
    if (isDinnerTime())
        activeMeal = 'dinner';
    else
        // else if(isLunchTime()) use in deployment
        activeMeal = 'lunch';

    url += "?meal=" + activeMeal;
    url += "&location=" + activeDhall;
    url += "&start=now";
    url += "&end=" + endTime;
    url += "&atdhall=True";

    submitButtonForm.setAttribute('href', url);

};



function length(t1, t2) {
    let hour1 = Number(t1.substring(0, 2));
    let hour2 = Number(t2.substring(0, 2));
    let min1 = Number(t1.substring(3));
    let min2 = Number(t2.substring(3));

    let time1 = new Date();
    let time2 = new Date();
    time1.setHours(hour1);
    time1.setMinutes(min1);
    time2.setHours(hour2);
    time2.setMinutes(min2);

    let millis = time2.getTime() - time1.getTime();
    return millis / (1000 * 60);
}


// compare times in string format HH:MM
function compareTimeStrings(t1, t2) {
    let hour1 = Number(t1.substring(0, 2));
    let hour2 = Number(t2.substring(0, 2));
    let min1 = Number(t1.substring(3));
    let min2 = Number(t2.substring(3));

    if (hour1 != hour2) return hour1 - hour2;
    else
        return min1 - min2;
};




// validate request fields, prevent submission if invalid
submitButtonForm.addEventListener('click', function (event) {


    let endTime = document.getElementById("endTimeButton").value;
    console.log(endTime);

    // determine if any dhall buttons have been pressed 'ON'
    let selected = activeDhall != ""

    console.log(activeDhall)

    // check if 
    let validMealTimes = validateTimes(endTime);

    console.log('valid mealtimes ' + validMealTimes)
    console.log('lunch time? : ' + isLunchTime())
    console.log('dinner time? : ' + isDinnerTime())



    document.getElementById('errorBox').innerHTML = ""

    let emptyFields = (endTime === "" || !selected)

    let interval_len = 20;
    let startTime = new Date().toTimeString().substring(0, 5);
    let longEnoughInterval = length(startTime, endTime) >= interval_len;
    console.log('long enough interval?: ' + longEnoughInterval)

    console.log('empty: ' + emptyFields)

    // takeout validMealTimes to remove lunch/dinner time validation
    if (emptyFields || !validMealTimes || !longEnoughInterval) {
        console.log('attempt to send invalid meal request')
        if (emptyFields)
            document.getElementById('errorBox').innerHTML += "<p>*Please select all fields to make a match request</p><br>"
        else if (!validMealTimes && (isLunchTime() || isDinnerTime()))
        document.getElementById('errorBox').innerHTML += "<p>*The dining hall may not be open for the current mealtime at these hours. <br> Please refer to the dining hall hours enter valid times for a match request.</p><br>"
        if (!isLunchTime() && !isDinnerTime() && !emptyFields)
            document.getElementById('errorBox').innerHTML += '<p>*On demand meal requests cannot be made outside of dining hall hours. <br> Please try <a href = "/schedule" >scheduling a meal</a> or try again later.</p><br>'
        if (!longEnoughInterval && !emptyFields)
            document.getElementById('errorBox').innerHTML += "<p>*Please enter a time interval of at least " + interval_len + " minutes</p><br>"
        // prevents submission
        event.preventDefault();
    }
    else {
        console.log('submission successful')
        updateUrl()
    }


});

function validateTimes(t1) {
    console.log("validation, time: " + t1)
    if (t1 === "") return false;
    else {


        let nowTime = new Date().toTimeString().substring(0, 5);
        console.log('cur time', nowTime)

        // if dinner time, ensure endTime is in dinner hour range and is later than present time
        let dinner_bool = isDinnerTime() &&
            (compareTimeStrings(nowTime, t1) <= 0) &&
            (compareTimeStrings(t1, "20:00") <= 0);
        console.log("RETURN ME, dinner: " + dinner_bool);
        
        // if lunch time, ensure endTime is in lunch hour range and is later than present time
        let lunch_bool = isLunchTime() &&
            (compareTimeStrings(nowTime, t1) <= 0) &&
            (compareTimeStrings(t1, "14:00") <= 0);
        console.log("RETURN ME, lunch: " + lunch_bool);
        
        return lunch_bool || dinner_bool;

    }
}



let endTimeButton = document.getElementById("endTimeButton");


endTimeButton.addEventListener('click', updateUrl);
// update url on changing times
endTimeButton.addEventListener('change', updateUrl);

for (let i = 0; i < dHallButtons.length; i++)
    dHallButtons[i].addEventListener('click', updateUrl)


function addAnyTimeButton() {
    
    var nowTime = (new Date()).toLocaleTimeString('en-GB').substring(0,5);
    
    if (isLunchTime() || isDinnerTime())
    {
        // add anyTime button
        var buttonString = '<button type="button" class="btn-sm" id = "anyTime" style = "margin-left: 10px;" data-toggle="tooltip" data-placement="bottom" title="Add the full time window for the selected meal period." onclick = "updateAnyTimes()">Rest of ';
        if (isLunchTime())
            buttonString += "Lunch </button>";
        else if (isDinnerTime())
        buttonString += "Dinner </button>";
        document.getElementById('time').innerHTML += buttonString;
        console.log("any time button added ");
    }
}

addAnyTimeButton()

function updateAnyTimes()
    {
        
        var nowTime = (new Date()).toLocaleTimeString('en-GB').substring(0,5);
        console.log(nowTime);

        
        if (isLunchTime())
            document.getElementById('endTimeButton').setAttribute('value', '14:00');
        else if (isDinnerTime())
            document.getElementById('endTimeButton').setAttribute('value', '20:00');
        
    }


// document.getElementById('anyTime').addEventListener('mouseover', function(){anyTimeButton.style.backgroundColor = "#ff9f46";});
// document.getElementById('anyTime').addEventListener('mouseout', function(){anyTimeButton.style.backgroundColor = "";} );


    // activate tooltips
$('#anyTime').ready(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

