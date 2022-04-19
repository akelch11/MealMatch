function isWeekend() {
    let dayOfWeek = (new Date()).getDay();
    return (dayOfWeek == 6) || (dayOfWeek == 0);
}

function updateTimeBoundaries(meal) {
    let startTimeEL = document.getElementById('startTimeButton')
    let endTimeEL = document.getElementById('endTimeButton')
    let dateTime = new Date();
    // format string 
    curr = ("0" + dateTime.getHours()).slice(-2) + ":" + ("0" + dateTime.getMinutes()).slice(-2)
    if (meal === "dinner") {
        endTimeEL.setAttribute('max', '20:00');
        endTimeEL.setAttribute('min', curr);
        // startTimeEL.setAttribute('min', curr); TODO
        // startTimeEL.setAttribute('max', smthng);
    }
    else if (isLunchTime()) {
        endTimeEL.setAttribute('max', '14:00');
        endTimeEL.setAttribute('min', curr);
        // startTimeEL.setAttribute('min', curr); TODO
        // startTimeEL.setAttribute('max', smthng);
    }
}