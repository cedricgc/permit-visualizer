var buttons = ["Building", "Plumbing", "Electrical", "Mechanical", "Driveway"]
var loadurl;

var heatmap;
var pointData;


function reloadMap(){
  pointData.clear();
  var url = "api/v1/heatmap?";
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
  restConnect(url);
  return false;
}

function restConnect(url) {
  loadurl = url;
  $.getJSON(url, displayData);
}

function displayData(data) {
  var cursor = data.cursor;
  var count = data.count;
  if(cursor != null) {
    addHeatmapPoints(data);
    $.getJSON(loadurl + "&after=" + cursor, displayData);
  }
   window.localStorage.clear();
}

function addHeatmapPoints(data) {
  for(var i = 0; i < data.count; i++) {
    if(data.data[i].latitude != null && data.data[i].longitude != null) {
      pointData.push(
        new google.maps.LatLng(data.data[i].latitude, data.data[i].longitude)
      );
      console.log(pointData.size);
    }
  }
}

function createHeatmap(map) {
  pointData = new google.maps.MVCArray();
  heatmap = heatmap = new google.maps.visualization.HeatmapLayer({
    data: pointData,
    map: map
  });
  heatmap.setMap(map);
}
