// loading animations
function loadingAnimationFade() {
  $('#loading').animate({opacity: '0.2'}, 800);
  $('#loading').animate({opacity: '1'}, 800, loadingAnimationFade);
}

function loadingAnimationSlide() {
  $('#loading2').animate({'margin-right': '-=50px'}, 400);
  $('#loading2').animate({'margin-left': '-=50px'}, 400, loadingAnimationSlide);
}

$(document).bind('ajaxSend', function() {
  $('#loading-icons').css('visibility', 'visible');
  // $('#loading2').fadeIn(400).show();
  // loadingAnimationFade();
  // loadingAnimationSlide();
});

$(document).bind('ajaxComplete', function() {
  $('#loading-icons').css('visibility', 'hidden');
  // $('#loading2').empty();
});

function formatDate(datetime) {
  let date = new Date(datetime)
  date_split = date.toString().split(" ")
  return date_split
}

// event search with user artists
$('#event-search').on('submit', (evt) => {
  evt.preventDefault();
  console.log('submitted')

  const formInputs = {
    'city': $('#city').val(),
    'distance': $('#distance').val()
  };

  $.post('/event-search', formInputs, (results) => {
    console.log(results);
    if (results.length >= 1) {
      $('#event-header').html('<h1><b>Events near you</b></h1><br>')
      for (let result of results) {
        formattedDate = formatDate(result['starts_at'])
        $('#event-results').append(`
          <div class="event-div" id="yellow-bg">
              <div class="rect-img img-fluid">
                <img class="event-img" src="${result['img']}">
              </div>
              <div class="event-text">
                <div class="row">
                  <div class="col-3 text-center">
                    <p>${formattedDate[1]}</p>
                    <h2>${formattedDate[2]}</h2>
                  </div>
                  <div class="col-9">
                    <h4>${result['name']}</h4>
                    <p>${result['venue']}</p>
                    <a class="btn btn-info" href="${result['url']}" target="_blank">RSVP on Eventbrite</a>
                  </div>
                </div>
              </div>
            </div>
          `)
          $('#search-again').show();
      }
    } else {
      $('#none-found').show();
      $('#search-again').show();
    }
  });
  $('input[type=submit]').hide();
});


// event search with recommended events
$('#recommended').on('submit', (evt) => {
  evt.preventDefault();
  $('#none-found').hide();

  const formInputs = {
    'city': $('#city').val(),
    'distance': $('#distance').val()
  };

  $.post('/recommended', formInputs, (results) => {
    console.log(results)
    if (results) {
      // $('#event-results').append('<h2>You might like</h2>')
      for (let result of results) {
        formattedDate = formatDate(result['starts_at'])
        $('#event-results').append(`
          <div class="event-div" id="orange-bg">
              <div class="rect-img img-fluid">
                <img class="event-img" src="${result['img']}">
              </div>
              <div class="event-text">
                <div class="row">
                  <div class="col-3 text-center">
                    <p>${formattedDate[1]}</p>
                    <h2>${formattedDate[2]}</h2>
                  </div>
                  <div class="col-9">
                    <h4>${result['name']}</h4>
                    <p>${result['venue']}</p>
                    <a class="btn btn-info" href="${result['url']}" target="_blank">RSVP on Eventbrite</a>
                  </div>
                </div>
              </div>
            </div>
          `)
      }
    } else {
      $('#none-found').show()
    }
  });
  $('input[type=submit]').hide();
});


$('#search-again').on('click', () => {
  $('#event-header').empty();
  $('#event-results').empty();
  $('input[type=submit]').show();
  // $('#search-area').show();
  // $('#search-area2').show();
  $('#search-again').hide();
})
