    let lunchButton = document.getElementById("lunchButton");
	let dinnerButton = document.getElementById("dinnerButton");
	let activeMeal = "";
	let activeDhalls = {};
	let dHallButtons = document.getElementsByClassName('dHallType');
	let anyDhallButton = document.getElementById('anyDhall');
	// is anyDhall active
	let isAnyActive = false;

	for (btn of dHallButtons) {
		activeDhalls[btn.id] = false;
	}


	lunchButton.addEventListener('click', function onClick() {
		activeMeal = 'lunch';
		// console.log('lunch Pressed');
		lunchButton.style.backgroundColor = "#ff9f46";
		dinnerButton.style.backgroundColor = '';

	});

	dinnerButton.addEventListener('click', function onClick() {
		activeMeal = 'dinner';
		// console.log('dinner Pressed');
		dinnerButton.style.backgroundColor = "#ff9f46";
		lunchButton.style.backgroundColor = '';

	});

	function detectBrunch() {
		
		// console.log("brunch function run")
		now = new Date()
		// render "Brunch" on weekends
		if (now.getDay() == 0 || now.getDay() == 6)
			lunchButton.value = "Brunch"
	}

	$("document").ready(detectBrunch())

	for (let i = 0; i < dHallButtons.length; i++) {
		let btn = dHallButtons[i];
		btn.addEventListener('click',
			function () {

				dhall = btn.id;

				// select Dhall
				if (!activeDhalls[dhall]) {
					btn.style.backgroundColor = "#ff9f46";
					activeDhalls[dhall] = true;
				}
				else {
					btn.style.backgroundColor = "";
					activeDhalls[dhall] = false;
				}

				// deactivate anyDHall button
				if(isAnyActive)
				{
					anyDhallButton.style.backgroundColor = "";
					isAnyActive = false;
				
				}
				

				// console.log(activeDhalls)

			});
	}

	anyDhallButton.addEventListener('click',
		function(){

			if(!isAnyActive)
				anyDhallButton.style.backgroundColor = "#ff9f46";
			else
				anyDhallButton.style.backgroundColor = "";
				
			for(let i = 0; i < dHallButtons.length; i++)
			{
				let btn = dHallButtons[i];
				
				// activate all buttons
				if(!isAnyActive)
					{
						activeDhalls[btn.id] = true;
						btn.style.backgroundColor = "#ff9f46";
					}
				else // deactivate all buttons
					{
						activeDhalls[btn.id] = false;
						btn.style.backgroundColor = "";
					}
			}
			// flip active flag
			isAnyActive = !isAnyActive;
		});

	let submitButtonForm = document.getElementById("submitButtonForm");

	// update url to contain proper match request information
	function updateUrl() {
		let url = "/submitrequest"
		let startTime = document.getElementById("startTimeButton").value;
		let endTime = document.getElementById("endTimeButton").value;


		url += "?meal=" + activeMeal;
		url += "&location=";

		let dHallSelected = false;
		let dHallOptions = "";
		for (var dh in activeDhalls) {
			if (activeDhalls[dh]) {
				dHallOptions += (dh + "-");
				dHallSelected = true;
			}
		}

		// only update url if time, meal type, and location are all specified
		url += dHallOptions.slice(0, -1);
		url += "&start=" + startTime;
		url += "&end=" + endTime;
		url += "&atdhall=False";

		submitButtonForm.setAttribute('href', url);
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

	// return the length of time between t1 and t2 in minutes
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
	function validateTimes(t1, t2, meal) {

		if (t1 === "" || t2 === "" || meal === "") return false;
		else {


			let now = new Date();
			let nowTime = now.toTimeString().substring(0, 5);


			// on Saturday or Sunday (weekends)
			// on weekends, brunch/lunch starts at 10AM
			let lunch_start;
			if (now.getDay() == 0 || now.getDay() == 6)
				lunch_start = "10:00";
			else // on weekdays, 11:30
				lunch_start = "11:30";

			// times are within lunch range and not in past
			let lunch_bool = (meal === 'lunch') &&
				(compareTimeStrings(lunch_start, t1) <= 0) &&
				(compareTimeStrings(nowTime, t1) <= 0) &&
				(compareTimeStrings(t1, t2) < 0) &&
				(compareTimeStrings(t2, "14:00") <= 0);

			// times are within dinner range and not in past
			let dinner_bool = (meal === "dinner") &&
				(compareTimeStrings("17:00", t1) <= 0) &&
				(compareTimeStrings(nowTime, t1) <= 0) &&
				(compareTimeStrings(t1, t2) < 0) &&
				(compareTimeStrings(t2, "20:00") <= 0);

			return lunch_bool || dinner_bool;
		}
	}

	// validate request fields, prevent submission if invalid
	submitButtonForm.addEventListener('click', function (event) {

		let startTime = document.getElementById("startTimeButton").value;
		let endTime = document.getElementById("endTimeButton").value;
		// console.log(startTime + " " + endTime);

		// determine if any dhall buttons have been pressed 'ON'
		let selected = false;
		for (var dh in activeDhalls)
			if (activeDhalls[dh])
				selected = true;

		// console.log('dHallselected' + selected)

		// check if times are within the reasonable range and ordered correctly
		let validMealTimes = validateTimes(startTime, endTime, activeMeal);
		// console.log('valid mealtimes ' + validMealTimes)

		let emptyFields = (endTime === "" || startTime === "" || activeMeal === "" || !selected)
		// console.log('empty fields?: ' + emptyFields)
		
		let interval_len = 20;
		let longEnoughInterval = length(startTime, endTime) >= interval_len;
		// console.log('long enough interval?: ' + longEnoughInterval)

		document.getElementById('errorBox').innerHTML = ""
		// takeout validMealTimes to remove lunch/dinner time validation
		if (emptyFields || !validMealTimes || !longEnoughInterval) {
			// console.log('attempt to send invalid meal request')
			// if there is an incomplete field, only show this error
			if (emptyFields)
				document.getElementById('errorBox').innerHTML += "<p>*Please enter all information to make a match request</p><br>"
			// otherwise, if times are not appropriate, prompt user to enter valid hours
			else if (!validMealTimes)
				{
					var nowTimeStr = (new Date()).toLocaleTimeString('en-GB').substring(0,5);
					if ((compareTimeStrings(nowTimeStr, "14:00") > 0 && activeMeal == 'lunch') || 
						((compareTimeStrings(nowTimeStr, "20:00")  > 0) && activeMeal == 'dinner'))
					  	 document.getElementById('errorBox').innerHTML += "<p>*The hours of the selected mealtime have passed.<br> Please refer to the dining hall hours to enter valid times for a match request.</p><br>"
					else
					document.getElementById('errorBox').innerHTML += "<p>*The dining hall may not be open for the selected meal at these hours.<br> Please refer to the dining hall hours to enter valid times for a match request.</p><br>"
				}

		
			// if time entered isn't long enough and all fields complete
			if (!longEnoughInterval && !emptyFields)
				document.getElementById('errorBox').innerHTML += "<p>*Please enter a time interval of at least " + interval_len + " minutes to make a request</p><br>"

			// prevents submission
			event.preventDefault();
		}
		else updateUrl();
	});



	lunchButton.addEventListener('click', updateUrl);
	dinnerButton.addEventListener('click', updateUrl);

	for (let i = 0; i < dHallButtons.length; i++)
		dHallButtons[i].addEventListener('click', updateUrl)

	let startTimeButton = document.getElementById("startTimeButton");
	let endTimeButton = document.getElementById("endTimeButton");
	startTimeButton.addEventListener('click', updateUrl);
	endTimeButton.addEventListener('click', updateUrl);
	// update url on changing times
	startTimeButton.addEventListener('change', updateUrl);
	endTimeButton.addEventListener('change', updateUrl)


	
	function addAnyTimeButton() {
		
		var nowTime = (new Date()).toLocaleTimeString('en-GB').substring(0,5);
		
		if (compareTimeStrings(nowTime, "20:00") < 0)
		{
			// add anyTime button
			document.getElementById('time').innerHTML += '<button type="button" class="btn-sm" id = "anyTime" style = "margin-left: 10px; " data-toggle="tooltip" data-placement="right" title="Add the full time window for the selected meal period." onclick = "updateAnyTimes()">Rest of Meal</button>';
			// console.log("any time button added " + (compareTimeStrings(nowTime, "20:00") < 0));
		}
	}

	addAnyTimeButton();
	
	
	let anyTimeButton = document.getElementById('anyTime');
		function updateAnyTimes()
		{
			
			var nowTime = (new Date()).toLocaleTimeString('en-GB').substring(0,5);
			// console.log(nowTime);

			if(activeMeal === "lunch")
			{
				if (isLunchTime())
					document.getElementById('startTimeButton').setAttribute('value', nowTime);
				else 
				{
					if (isWeekend())
					document.getElementById('startTimeButton').setAttribute('value', "10:00")
					else
					document.getElementById('startTimeButton').setAttribute('value', "11:30")
				}
					
				document.getElementById('endTimeButton').setAttribute('value', "14:00");


				// console.log('times changed to lunch')
			}
			else if (activeMeal === "dinner")
			{
				if (isDinnerTime())
					document.getElementById('startTimeButton').setAttribute('value', nowTime);
				else 
				{
					document.getElementById('startTimeButton').setAttribute('value', "17:00")
				}
				
				document.getElementById('endTimeButton').setAttribute('value', "20:00");

				// console.log('times changed to dinner')
			}

			startTimeButton.innerHTML = startTimeButton.innerHTML;
			endTimeButton.innerHTML = endTimeButton.innerHTML;

		}

	anyTimeButton.addEventListener('mouseover', function(){anyTimeButton.style.backgroundColor = "#ff9f46";});
	anyTimeButton.addEventListener('mouseout', function(){anyTimeButton.style.backgroundColor = "";} );



	function updateCurrentMealtimeDisplay(){
		
		var hoursBox = $('#hoursBox')
		if(isLunchTime())
		{
			if (isWeekend())
				hoursBox.innerHTML = "Current Mealtime: Brunch";
			else
			hoursBox.innerHTML = "Current Mealtime: Lunch";

		}
		else if (isDinnerTime())
			hoursBox.innerHTML = "Current Mealtime: Dinner";
		else
		hoursBox.innerHTML = "";
	}

	