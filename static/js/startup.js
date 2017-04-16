function startup() {
  setupTime();
}

function setupTime() {
  var today = new Date();
  var day = today.getDate();
  var month = today.getMonth()+1;
  var year = today.getFullYear();
  if(month < 10) {
    month = "0" + month;
  }
  if(day < 10) {
    day = "0" + day;
  }
  var todaysDate = year + "-" + month + "-" + day;
  var prevDate = year-1 + "-" + month + "-" + day;
  $('#date1').val(prevDate);
  $('#date2').val(todaysDate);
}
