
var buttons = ["Building", "Plumbing", "Electrical", "Mechanical", "Driveway"]
var bgColor = [
    'rgba(255, 153, 51, 0.2)',
    'rgba(51, 51, 255, 0.2)',
    'rgba(255, 51, 153, 0.2)',
    'rgba(51, 255, 51, 0.2)',
    'rgba(255, 255, 51, 0.2)',
    'rgba(204, 0, 0, 0.2)'
]

var bgBorder = [
  'rgba(255, 153, 51, 1)',
  'rgba(51, 51, 255, 1)',
  'rgba(255, 51, 153, 1)',
  'rgba(51, 255, 51, 1)',
  'rgba(255, 255, 51, 1)',
  'rgba(204, 0, 0, 1)'
]

var globBarChart = null;

function startup() {
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

  $("#date1").val('1900-01-01');
  $("#date2").val(todaysDate);
  $("#Building").attr('checked', true);
  $("#Plumbing").attr('checked', true);
  $("#Electrical").attr('checked', true);

  reloadGraph();
}


function reloadGraph() {
  $(".overlay").show();
  var url = "api/v1/count?";
  var arrayLength = buttons.length;
  for (var i = 0; i < arrayLength; i++) {
    if($('#' + buttons[i]).is(":checked")) {
      if(i != 4) {
        url += "type=" + buttons[i] + "%20Permit&";
      }
      else {
        url += "type=" + buttons[i] + "%20%2F%20Sidewalks&";
      }
    }
  }
  if($('#Demolition').is(":checked")) {
    url += 'class=Demolition&';
  }
  var start = $('#date1').val();
  var end = $('#date2').val();

  if(moment(start, "YYYY-MM-DD", true).isValid()) {
    url += "start=" + start;
  }
  else {
    alert("Start Date is not valid");
    return false;
  }
  if(moment(end, "YYYY-MM-DD", true).isValid()) {
    url += "&end=" + end;
  }
  else {
    alert("End Date is not valid");
    return false;
  }
  var m = moment.utc(start, "YYYY-MM-DD");
  if(m.isAfter(end)) {
    alert("End Date must be after Start Date");
    return false;
  }
  $.getJSON(url, loadData);
  return false;

}

function loadData(data) {
  var years = [];
  var counts = [];
  var barTemp = [];
  var borderTemp = [];
  var barColor = [];
  var borderColor = [];

  for (var i = 0; i < buttons.length; i++) {
    if($('#' + buttons[i]).is(":checked")) {
      barTemp.push(bgColor[i]);
      borderTemp.push(bgBorder[i]);
    }
  }


  for(var i = 0; i < data.count; i ++) {
    years.push(data.data[i].year);
    counts.push(data.data[i].count);
    barColor.push(barTemp[i%barTemp.length]);
    borderColor.push(borderTemp[i%borderTemp.length])
  }
  createGraph(years, counts, barColor, borderColor);
}

function createGraph(years, counts, barColor, borderColor) {
  refreshCanvas();
  var ctx = document.getElementById("myChart").getContext('2d');
  ctx.canvas.height = 55;
  var data = {
      labels: years,
      datasets: [
          {
              label: "Number of Permits per Year",
              backgroundColor: barColor,
              borderColor: borderColor,
              borderWidth: 1,
              data: counts
          }
      ]
  };

  globBarChart = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        scales: {
            xAxes: [{
                stacked: true
            }],
            yAxes: [{
                stacked: true
            }]
        }
      }
    }
  );
  $(".overlay").hide();
}

function refreshCanvas() {
  $('#myChart').remove();
  $('#graph-container').append('<canvas id="myChart" width="100%" height="100%" style="min-height: 500px"></canvas>');
}
